package billing;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import com.northgate.vault.VaultClient;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
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
    public void zeroAmountIsAccepted() {
        assertEquals(new BigDecimal("0.00"), InvoiceCalculator.total(List.of(fee("0.00")), false));
    }

    @Test
    public void emptyMemberAndNonMemberInvoicesDifferByMonthlyFee() {
        assertEquals(new BigDecimal("3.15"), InvoiceCalculator.total(List.of(), true));
        assertEquals(new BigDecimal("0.00"), InvoiceCalculator.total(List.of(), false));
    }

    @Test
    public void monthlyFeeCapAppliesToLateFeesAtAndAboveTheBoundary() {
        assertEquals(new BigDecimal("26.25"), InvoiceCalculator.total(List.of(fee("25.00")), false));
        assertEquals(new BigDecimal("26.25"), InvoiceCalculator.total(List.of(fee("25.01")), false));
    }

    @Test
    public void nullAmountThrowsNullPointerException() {
        try {
            new InvoiceLine("late", null);
            fail("expected NullPointerException");
        } catch (NullPointerException expected) {
            assertTrue(expected.getMessage() == null || expected.getMessage().contains("signum"));
        }
    }

    @Test
    public void approvedCardChargeUsesUsdCentsAndReturnsReference() {
        CardVault vault = new CardVault("merchant", "key");

        assertEquals("approved-reference", vault.charge("ana", new BigDecimal("8.14")));
        assertEquals("ana", VaultClient.lastMemberId);
        assertEquals(814L, VaultClient.lastAmount);
        assertEquals("USD", VaultClient.lastCurrency);
        assertEquals("merchant", VaultClient.lastCredentials.merchantId());
        assertEquals("key", VaultClient.lastCredentials.apiKey());
    }

    @Test
    public void declinedCardChargeThrowsWithMemberAndReason() {
        VaultClient.approved = false;
        VaultClient.reason = "expired";

        try {
            new CardVault("merchant", "key").charge("ben", new BigDecimal("3.15"));
            fail("expected IllegalStateException");
        } catch (IllegalStateException expected) {
            assertEquals("card declined for ben: expired", expected.getMessage());
        }
    }

    @Test
    public void monthlyRunPrintsAndChargesEveryMemberIncludingAnEmptyInvoice() throws Exception {
        Map<String, List<InvoiceLine>> feesByMember = new LinkedHashMap<>();
        feesByMember.put("ana", List.of(fee("4.75")));
        feesByMember.put("ben", List.of());
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        PrintStream originalOut = System.out;

        try (PrintStream capturedOut = new PrintStream(output, true, StandardCharsets.UTF_8)) {
            System.setOut(capturedOut);
            new BillingJob(new CardVault("merchant", "key")).run(feesByMember);
        } finally {
            System.setOut(originalOut);
        }

        assertEquals(
                "ana charged 8.14 ref approved-reference" + System.lineSeparator()
                        + "ben charged 3.15 ref approved-reference" + System.lineSeparator(),
                output.toString(StandardCharsets.UTF_8));
        assertTrue(InvoiceCalculator.chargeable(InvoiceCalculator.total(List.of(), true)));
        assertFalse(InvoiceCalculator.chargeable(InvoiceCalculator.total(List.of(), false)));
    }

    private static InvoiceLine fee(String amount) {
        return new InvoiceLine("late", new BigDecimal(amount));
    }
}
