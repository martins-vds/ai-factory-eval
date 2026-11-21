package billing;

import com.northgate.vault.VaultClient;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class BillingCharacterization {
    private static int cases;
    private static int matches;
    private static int differs;

    private BillingCharacterization() {
    }

    private static InvoiceLine line(String amount) {
        return new InvoiceLine("late", new BigDecimal(amount));
    }

    private static void record(String name, String predicted, String observed, boolean matchesPrediction) {
        cases++;
        if (matchesPrediction) {
            matches++;
        } else {
            differs++;
        }
        System.out.println(name + "|predicted=" + predicted + "|observed=" + observed +
                "|match=" + matchesPrediction);
    }

    private static String exceptionOf(Runnable runnable) {
        try {
            runnable.run();
            return "NO_EXCEPTION";
        } catch (RuntimeException e) {
            return e.getClass().getSimpleName();
        }
    }

    private static String captureOutput(Runnable runnable) {
        PrintStream original = System.out;
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (PrintStream capture = new PrintStream(bytes)) {
            System.setOut(capture);
            runnable.run();
        } finally {
            System.setOut(original);
        }
        return bytes.toString();
    }

    public static void main(String[] args) throws Exception {
        record("invoice-line-normal",
                "description=late amount=4.75", 
                "description=" + line("4.75").description() + " amount=" + line("4.75").amount(),
                line("4.75").amount().compareTo(new BigDecimal("4.75")) == 0);
        record("invoice-line-negative",
                "IllegalArgumentException",
                exceptionOf(() -> line("-1.00")),
                exceptionOf(() -> line("-1.00")).equals("IllegalArgumentException"));
        record("invoice-line-null",
                "NullPointerException",
                exceptionOf(() -> new InvoiceLine("late", null)),
                exceptionOf(() -> new InvoiceLine("late", null)).equals("NullPointerException"));
        record("invoice-line-zero",
                "accepted at zero",
                exceptionOf(() -> line("0")),
                exceptionOf(() -> line("0")).equals("NO_EXCEPTION"));

        record("invoice-total-member-normal",
                "8.14",
                InvoiceCalculator.total(List.of(line("4.75")), true).toPlainString(),
                InvoiceCalculator.total(List.of(line("4.75")), true).compareTo(new BigDecimal("8.14")) == 0);
        record("invoice-total-fee-cap",
                "29.40",
                InvoiceCalculator.total(List.of(line("20.00"), line("12.50")), true).toPlainString(),
                InvoiceCalculator.total(List.of(line("20.00"), line("12.50")), true).compareTo(new BigDecimal("29.40")) == 0);
        record("invoice-total-fee-cap-exact",
                "29.40",
                InvoiceCalculator.total(List.of(line("25.00")), true).toPlainString(),
                InvoiceCalculator.total(List.of(line("25.00")), true).compareTo(new BigDecimal("29.40")) == 0);
        record("invoice-total-empty-member",
                "3.15",
                InvoiceCalculator.total(List.of(), true).toPlainString(),
                InvoiceCalculator.total(List.of(), true).compareTo(new BigDecimal("3.15")) == 0);
        record("invoice-total-empty-nonmember",
                "0.00",
                InvoiceCalculator.total(List.of(), false).toPlainString(),
                InvoiceCalculator.total(List.of(), false).compareTo(new BigDecimal("0.00")) == 0);
        record("invoice-total-nonmember",
                "2.10",
                InvoiceCalculator.total(List.of(line("2.00")), false).toPlainString(),
                InvoiceCalculator.total(List.of(line("2.00")), false).compareTo(new BigDecimal("2.10")) == 0);
        record("invoice-total-half-up",
                "0.53",
                InvoiceCalculator.total(List.of(line("0.50")), false).toPlainString(),
                InvoiceCalculator.total(List.of(line("0.50")), false).compareTo(new BigDecimal("0.53")) == 0);

        record("chargeability-zero",
                "false",
                String.valueOf(InvoiceCalculator.chargeable(new BigDecimal("0"))),
                !InvoiceCalculator.chargeable(new BigDecimal("0")));
        record("chargeability-99-cents",
                "false",
                String.valueOf(InvoiceCalculator.chargeable(new BigDecimal("0.99"))),
                !InvoiceCalculator.chargeable(new BigDecimal("0.99")));
        record("chargeability-exact-dollar",
                "true",
                String.valueOf(InvoiceCalculator.chargeable(new BigDecimal("1.00"))),
                InvoiceCalculator.chargeable(new BigDecimal("1.00")));
        record("chargeability-above-dollar",
                "true",
                String.valueOf(InvoiceCalculator.chargeable(new BigDecimal("1.001"))),
                InvoiceCalculator.chargeable(new BigDecimal("1.001")));

        VaultClient.reset();
        VaultClient.approve("ref-accepted");
        final CardVault approvedVault = new CardVault("merchant", "key");
        record("card-vault-approved",
                "ref-accepted; minor=814; currency=USD",
                approvedVault.charge("ana", new BigDecimal("8.14")) + "; minor=" + VaultClient.lastMinorUnits() +
                        "; currency=" + VaultClient.lastCurrency(),
                approvedVault.charge("ana", new BigDecimal("8.14")).equals("ref-accepted") &&
                        VaultClient.lastMinorUnits() == 814 &&
                        "USD".equals(VaultClient.lastCurrency()));
        VaultClient.reset();
        final CardVault declinedVault = new CardVault("merchant", "key");
        VaultClient.decline("insufficient funds");
        record("card-vault-declined",
                "IllegalStateException",
                exceptionOf(() -> declinedVault.charge("ana", new BigDecimal("8.14"))),
                exceptionOf(() -> declinedVault.charge("ana", new BigDecimal("8.14"))).equals("IllegalStateException"));

        VaultClient.reset();
        VaultClient.approve("ref-batch");
        final CardVault batchVault = new CardVault("merchant", "key");
        final BillingJob batchJob = new BillingJob(batchVault);
        final Map<String, List<InvoiceLine>> batch = new LinkedHashMap<>();
        batch.put("ana", List.of(line("4.75")));
        batch.put("ben", List.of());
        String output = captureOutput(() -> batchJob.run(batch));
        record("monthly-batch-charge-and-carry",
                "ana charged 8.14 ref-batch; ben charged 3.15 ref-batch",
                output.trim().replaceAll("\\n", " | "),
                output.contains("ana charged 8.14 ref ref-batch") &&
                        output.contains("ben charged 3.15 ref ref-batch"));

        VaultClient.reset();
        VaultClient.approve("ref-a");
        final CardVault memberVault = new CardVault("merchant", "key");
        final BillingJob memberJob = new BillingJob(memberVault);
        final Map<String, List<InvoiceLine>> memberBatch = new LinkedHashMap<>();
        memberBatch.put("ana", List.of(line("4.75")));
        memberBatch.put("ben", List.of());
        String memberOutput = captureOutput(() -> memberJob.run(memberBatch));
        record("monthly-batch-all-entries-are-members",
                "both totals include monthly fee",
                memberOutput.trim().replaceAll("\\n", " | "),
                memberOutput.contains("ana charged 8.14") &&
                        memberOutput.contains("ben charged 3.15"));

        VaultClient.reset();
        VaultClient.approve("unused");
        final CardVault declineVault = new CardVault("merchant", "key");
        final BillingJob declineJob = new BillingJob(declineVault);
        VaultClient.decline("card declined");
        final Map<String, List<InvoiceLine>> declineBatch = new LinkedHashMap<>();
        declineBatch.put("ana", List.of(line("4.75")));
        declineBatch.put("ben", List.of());
        String declineOutput = captureOutput(() -> {
            try {
                declineJob.run(declineBatch);
            } catch (IllegalStateException ignored) {
            }
        });
        record("monthly-batch-stops-on-decline",
                "ana prints nothing; ben is not processed",
                declineOutput.trim().replaceAll("\\n", " | "),
                declineOutput.isEmpty());

        VaultClient.reset();
        VaultClient.approve("ref-entrypoint");
        String entryOutput = captureOutput(() -> BillingJob.main(new String[0]));
        record("job-entrypoint-fixed-samples",
                "ana 4.75 charged 8.14; ben empty charged 3.15",
                entryOutput.trim().replaceAll("\\n", " | "),
                entryOutput.contains("ana charged 8.14 ref ref-entrypoint") &&
                        entryOutput.contains("ben charged 3.15 ref ref-entrypoint"));
        record("job-entrypoint-environment-credentials",
                "merchant=characterization-merchant key=characterization-key",
                "merchant=" + VaultClient.credentials().merchantId() +
                        " key=" + VaultClient.credentials().apiKey(),
                "characterization-merchant".equals(VaultClient.credentials().merchantId()) &&
                        "characterization-key".equals(VaultClient.credentials().apiKey()));

        System.out.println("AFS-RESULT cases=" + cases + " passing=" + matches + " failing=" + differs);
        if (differs != 0) {
            throw new AssertionError(differs + " characterization cases differed");
        }
    }
}
