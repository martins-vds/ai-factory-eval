package billing;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.math.BigDecimal;
import java.util.List;
import org.junit.Test;

public class InvoiceCalculatorCharacterizationTest {
    @Test
    public void emptyMemberInvoiceIncludesMonthlyFeeAndTax() {
        assertEquals(new BigDecimal("3.15"), InvoiceCalculator.total(List.of(), true));
    }

    @Test
    public void emptyNonMemberInvoiceIsZero() {
        assertEquals(new BigDecimal("0.00"), InvoiceCalculator.total(List.of(), false));
    }

    @Test
    public void zeroLateFeeIsAllowed() {
        assertEquals(new BigDecimal("0.00"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", BigDecimal.ZERO)), false));
    }

    @Test
    public void exactFeeCapBoundaryIncludesMonthlyFee() {
        assertEquals(new BigDecimal("29.40"),
                InvoiceCalculator.total(List.of(new InvoiceLine("late", new BigDecimal("25.00"))), true));
    }

    @Test
    public void oneDollarChargeThresholdIsInclusive() {
        assertFalse(InvoiceCalculator.chargeable(new BigDecimal("0.00")));
        assertFalse(InvoiceCalculator.chargeable(new BigDecimal("0.99")));
        assertTrue(InvoiceCalculator.chargeable(new BigDecimal("1.00")));
    }

    @Test(expected = NullPointerException.class)
    public void nullLineAmountFailsWithNullPointerException() {
        new InvoiceLine("late", null);
    }
}
