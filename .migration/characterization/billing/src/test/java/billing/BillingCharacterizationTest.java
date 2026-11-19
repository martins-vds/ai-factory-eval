package billing;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import com.northgate.vault.VaultClient;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.Before;
import org.junit.Test;

public class BillingCharacterizationTest {
    private static InvoiceLine fee(String amount) {
        return new InvoiceLine("late", new BigDecimal(amount));
    }

    @Before
    public void resetVault() {
        VaultClient.reset();
    }

    @Test
    public void invoiceTotalsCoverEmptyFeesCapAndTax() {
        assertEquals(new BigDecimal("3.15"), InvoiceCalculator.total(List.of(), true));
        assertEquals(new BigDecimal("0.00"), InvoiceCalculator.total(List.of(), false));
        assertEquals(new BigDecimal("29.40"),
                InvoiceCalculator.total(List.of(fee("20.00"), fee("12.50")), true));
        assertEquals(new BigDecimal("0.53"), InvoiceCalculator.total(List.of(fee("0.50")), false));
    }

    @Test
    public void invoiceLinesRejectNegativeAndAllowZero() {
        assertEquals(new BigDecimal("0.00"), fee("0.00").amount());
        IllegalArgumentException error = assertThrows(
                IllegalArgumentException.class, () -> fee("-0.01"));
        assertEquals("negative charge: late", error.getMessage());
    }

    @Test
    public void nullInvoiceLineAmountThrowsNullPointerException() {
        assertThrows(NullPointerException.class, () -> new InvoiceLine("late", null));
    }

    @Test
    public void chargeThresholdIsInclusiveAtOneDollar() {
        assertFalse(InvoiceCalculator.chargeable(new BigDecimal("0.99")));
        assertTrue(InvoiceCalculator.chargeable(new BigDecimal("1.00")));
        assertFalse(InvoiceCalculator.chargeable(new BigDecimal("-0.01")));
    }

    @Test
    public void cardVaultSubmitsExactUsdCentsAndReturnsReference() {
        CardVault vault = new CardVault("merchant", "key");

        assertEquals("ref-ana", vault.charge("ana", new BigDecimal("12.34")));
        assertEquals(new com.northgate.vault.VaultCredentials("merchant", "key"), VaultClient.credentials());
        assertEquals(List.of(new VaultClient.Charge("ana", 1234L, "USD")), VaultClient.charges());
    }

    @Test
    public void cardVaultDeclinesAndRejectsFractionalCents() {
        VaultClient.declineWith("do not honor");
        IllegalStateException error = assertThrows(
                IllegalStateException.class,
                () -> new CardVault("merchant", "key").charge("ben", new BigDecimal("1.00")));
        assertEquals("card declined for ben: do not honor", error.getMessage());
        assertThrows(
                ArithmeticException.class,
                () -> new CardVault("merchant", "key").charge("ben", new BigDecimal("1.001")));
    }

    @Test
    public void billingJobChargesEachMemberAndCarriesEmptyMemberFeesIntoMembershipTotal() {
        Map<String, List<InvoiceLine>> invoices = new LinkedHashMap<>();
        invoices.put("ana", List.of(fee("4.75")));
        invoices.put("ben", List.of());
        ByteArrayOutputStream output = captureOutput(() -> new BillingJob(new CardVault("m", "k")).run(invoices));

        assertEquals(
                "ana charged 8.14 ref ref-ana" + System.lineSeparator()
                        + "ben charged 3.15 ref ref-ben" + System.lineSeparator(),
                output.toString(StandardCharsets.UTF_8));
        assertEquals(
                List.of(
                        new VaultClient.Charge("ana", 814L, "USD"),
                        new VaultClient.Charge("ben", 315L, "USD")),
                VaultClient.charges());
    }

    @Test
    public void billingJobIsSilentForNoMembersAndPropagatesDeclines() {
        ByteArrayOutputStream emptyOutput =
                captureOutput(() -> new BillingJob(new CardVault("m", "k")).run(Map.of()));
        assertEquals("", emptyOutput.toString(StandardCharsets.UTF_8));
        assertTrue(VaultClient.charges().isEmpty());

        VaultClient.declineWith("blocked");
        Map<String, List<InvoiceLine>> invoices = Map.of("ana", List.of(fee("1.00")));
        assertThrows(
                IllegalStateException.class,
                () -> new BillingJob(new CardVault("m", "k")).run(invoices));
    }

    @Test
    public void entryPointReadsEnvironmentAndUsesFixedMembersRegardlessOfArguments() throws Exception {
        Path classes = Path.of(BillingJob.class.getProtectionDomain().getCodeSource().getLocation().toURI());
        ProcessBuilder builder = new ProcessBuilder(
                Path.of(System.getProperty("java.home"), "bin", "java").toString(),
                "-Dbilling.expectedMerchant=test-merchant",
                "-Dbilling.expectedKey=test-key",
                "-cp",
                classes.toString(),
                "billing.BillingJob",
                "ignored-argument");
        builder.environment().put("NORTHGATE_MERCHANT", "test-merchant");
        builder.environment().put("NORTHGATE_KEY", "test-key");
        builder.redirectErrorStream(true);
        Process process = builder.start();
        boolean finished = process.waitFor(10, TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
        }

        assertTrue("billing main did not finish", finished);
        assertEquals(0, process.exitValue());
        assertEquals(
                "ana charged 8.14 ref ref-ana" + System.lineSeparator()
                        + "ben charged 3.15 ref ref-ben" + System.lineSeparator(),
                new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8));
    }

    private static ByteArrayOutputStream captureOutput(ThrowingRunnable action) {
        PrintStream original = System.out;
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        try (PrintStream captured = new PrintStream(output, true, StandardCharsets.UTF_8)) {
            System.setOut(captured);
            action.run();
        } finally {
            System.setOut(original);
        }
        return output;
    }

    @FunctionalInterface
    private interface ThrowingRunnable {
        void run();
    }
}
