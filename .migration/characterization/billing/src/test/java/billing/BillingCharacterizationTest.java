package billing;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertThrows;

import com.northgate.vault.ChargeResult;
import com.northgate.vault.VaultClient;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.Before;
import org.junit.Test;

public class BillingCharacterizationTest {
    @Before
    public void resetVault() {
        VaultClient.reset();
    }

    @Test
    public void calculatorTotalsMemberAndNonMemberInvoices() {
        assertEquals(new BigDecimal("8.14"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", new BigDecimal("4.75"))), true));
        assertEquals(new BigDecimal("2.10"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", new BigDecimal("2.00"))), false));
    }

    @Test
    public void calculatorHandlesEmptyFeesAndCapBoundary() {
        assertEquals(new BigDecimal("3.15"), InvoiceCalculator.total(List.of(), true));
        assertEquals(new BigDecimal("0.00"), InvoiceCalculator.total(List.of(), false));
        assertEquals(new BigDecimal("26.25"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", new BigDecimal("25.00"))), false));
        assertEquals(new BigDecimal("26.25"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", new BigDecimal("25.01"))), false));
    }

    @Test
    public void calculatorRoundsTaxHalfUpAndUsesOneDollarThreshold() {
        assertEquals(new BigDecimal("0.53"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", new BigDecimal("0.50"))), false));
        assertFalse(InvoiceCalculator.chargeable(new BigDecimal("0.99")));
        assertTrue(InvoiceCalculator.chargeable(new BigDecimal("1.00")));
    }

    @Test
    public void calculatorFailsForNullFeeListAndNullFeeLine() {
        assertThrows(NullPointerException.class, () -> InvoiceCalculator.total(null, false));
        assertThrows(NullPointerException.class, () -> InvoiceCalculator.total(java.util.Arrays.asList((InvoiceLine) null), false));
    }

    @Test
    public void invoiceLineRejectsNegativeAmountWithDescription() {
        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> new InvoiceLine("late: L3", new BigDecimal("-1.00")));
        assertEquals("negative charge: late: L3", error.getMessage());
    }

    @Test
    public void invoiceLineAcceptsZeroAndExposesRecordComponents() {
        InvoiceLine line = new InvoiceLine("late", new BigDecimal("0.00"));
        assertEquals("late", line.description());
        assertEquals(new BigDecimal("0.00"), line.amount());
    }

    @Test
    public void invoiceLineFailsForNullAmountWithNullPointerException() {
        assertThrows(NullPointerException.class, () -> new InvoiceLine("late", null));
    }

    @Test
    public void billingJobChargesEachMemberInMapOrder() throws Exception {
        Map<String, List<InvoiceLine>> fees = new LinkedHashMap<>();
        fees.put("ana", List.of(new InvoiceLine("late", new BigDecimal("4.75"))));
        fees.put("ben", List.of());

        String output = captureOutput(() -> new BillingJob(new CardVault("merchant-test", "key-test")).run(fees));

        assertEquals("ana charged 8.14 ref test-reference" + System.lineSeparator()
                        + "ben charged 3.15 ref test-reference" + System.lineSeparator(),
                output);
        assertEquals(List.of(
                new VaultClient.Charge("ana", 814, "USD"),
                new VaultClient.Charge("ben", 315, "USD")), VaultClient.charges());
    }

    @Test
    public void billingJobDoesNothingForAnEmptyMap() throws Exception {
        String output = captureOutput(() -> new BillingJob(new CardVault("merchant-test", "key-test")).run(Map.of()));

        assertEquals("", output);
        assertTrue(VaultClient.charges().isEmpty());
    }

    @Test
    public void billingJobPropagatesDeclineAndSkipsLaterMembers() {
        VaultClient.setResult(new ChargeResult(false, "expired", ""));
        Map<String, List<InvoiceLine>> fees = new LinkedHashMap<>();
        fees.put("ana", List.of());
        fees.put("ben", List.of());

        IllegalStateException error = assertThrows(IllegalStateException.class,
                () -> new BillingJob(new CardVault("merchant-test", "key-test")).run(fees));

        assertEquals("card declined for ana: expired", error.getMessage());
        assertEquals(List.of(new VaultClient.Charge("ana", 315, "USD")), VaultClient.charges());
    }

    @Test
    public void billingJobRejectsNullMemberMap() {
        assertThrows(NullPointerException.class,
                () -> new BillingJob(new CardVault("merchant-test", "key-test")).run(null));
        assertTrue(VaultClient.charges().isEmpty());
    }

    @Test
    public void cardVaultConnectsAndSendsExactUsdCents() {
        CardVault vault = new CardVault("merchant-test", "key-test");

        assertEquals("test-reference", vault.charge("member-9", new BigDecimal("8.14")));
        assertEquals("merchant-test", VaultClient.connectedCredentials().merchantId());
        assertEquals("key-test", VaultClient.connectedCredentials().apiKey());
        assertEquals(List.of(new VaultClient.Charge("member-9", 814, "USD")), VaultClient.charges());
    }

    @Test
    public void cardVaultThrowsOnDecline() {
        VaultClient.setResult(new ChargeResult(false, "expired", ""));
        CardVault vault = new CardVault("merchant-test", "key-test");

        IllegalStateException error = assertThrows(IllegalStateException.class,
                () -> vault.charge("member-9", new BigDecimal("8.14")));

        assertEquals("card declined for member-9: expired", error.getMessage());
        assertEquals(List.of(new VaultClient.Charge("member-9", 814, "USD")), VaultClient.charges());
    }

    @Test
    public void cardVaultRejectsAmountsThatCannotBeConvertedToExactCents() {
        CardVault vault = new CardVault("merchant-test", "key-test");

        assertThrows(ArithmeticException.class, () -> vault.charge("member-9", new BigDecimal("1.001")));
        assertTrue(VaultClient.charges().isEmpty());
    }

    @Test
    public void buildTargetsJava17AndDeclaresThePrivateVaultDependency() throws Exception {
        String pom = Files.readString(sourcePath("pom.xml"));

        assertTrue(pom.contains("<maven.compiler.release>17</maven.compiler.release>"));
        assertTrue(pom.contains("<groupId>com.northgate.vault</groupId>"));
        assertTrue(pom.contains("<artifactId>vault-client</artifactId>"));
        assertTrue(pom.contains("https://maven.northgate-payments.internal/releases"));
    }

    @Test
    public void launcherPackagesBeforeUsingTheTargetDependencyWildcard() throws Exception {
        String script = Files.readString(sourcePath("run.sh"));

        assertTrue(script.contains("mvn -q -B package"));
        assertTrue(script.contains("target/classes:target/dependency/*"));
        assertTrue(script.contains("billing.BillingJob"));
    }

    private static Path sourcePath(String path) {
        return Path.of("../../../legacy-billing", path);
    }

    private static String captureOutput(ThrowingRunnable action) throws Exception {
        PrintStream originalOut = System.out;
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (PrintStream captured = new PrintStream(bytes, true, StandardCharsets.UTF_8)) {
            System.setOut(captured);
            action.run();
        } finally {
            System.setOut(originalOut);
        }
        return bytes.toString(StandardCharsets.UTF_8);
    }

    @FunctionalInterface
    private interface ThrowingRunnable {
        void run() throws Exception;
    }
}
