package billing;

import com.northgate.vault.VaultClient;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class CharacterizationHarness {
    private CharacterizationHarness() {
    }

    public static void main(String[] args) {
        VaultClient.reset();
        try {
            System.out.print(observe(args[0]));
        } catch (Throwable failure) {
            System.out.print(describe(failure));
        }
    }

    private static String observe(String scenario) {
        return switch (scenario) {
            case "line-zero" -> new InvoiceLine("late", new BigDecimal("0.00")).amount().toPlainString();
            case "line-negative" -> attempt(() -> new InvoiceLine("late", new BigDecimal("-1.00")));
            case "line-null" -> attempt(() -> new InvoiceLine("late", null));
            case "total-member" -> total(List.of(fee("4.75")), true);
            case "total-cap" -> total(List.of(fee("20.00"), fee("12.50")), true);
            case "total-nonmember" -> total(List.of(fee("2.00")), false);
            case "total-half-up" -> total(List.of(fee("0.50")), false);
            case "total-empty-member" -> total(List.of(), true);
            case "total-empty-nonmember" -> total(List.of(), false);
            case "total-null-list" -> attempt(() -> InvoiceCalculator.total(null, true));
            case "total-null-line" -> attempt(() -> InvoiceCalculator.total(Arrays.asList((InvoiceLine) null), true));
            case "charge-below" -> Boolean.toString(InvoiceCalculator.chargeable(new BigDecimal("0.99")));
            case "charge-boundary" -> Boolean.toString(InvoiceCalculator.chargeable(new BigDecimal("1.00")));
            case "charge-null" -> attempt(() -> InvoiceCalculator.chargeable(null));
            case "batch-empty" -> batch(Collections.emptyMap());
            case "batch-member-empty" -> batch(Map.of("member", List.of()));
            case "batch-multiple" -> batch(multipleMembers());
            case "batch-decline" -> declinedBatch();
            case "batch-null-map" -> attempt(() -> new BillingJob(new CardVault("merchant", "key")).run(null));
            case "batch-null-fees" -> attempt(() -> new BillingJob(new CardVault("merchant", "key"))
                    .run(Collections.singletonMap("member", null)));
            case "vault-approved" -> approvedVaultCharge(new BigDecimal("8.14"));
            case "vault-zero" -> approvedVaultCharge(new BigDecimal("0.00"));
            case "vault-negative" -> approvedVaultCharge(new BigDecimal("-1.00"));
            case "vault-fraction" -> vaultFailure(new BigDecimal("1.001"));
            case "vault-null" -> vaultFailure(null);
            case "vault-decline" -> declinedVaultCharge();
            case "entrypoint" -> entrypoint();
            default -> throw new IllegalArgumentException("unknown scenario: " + scenario);
        };
    }

    private static InvoiceLine fee(String amount) {
        return new InvoiceLine("late", new BigDecimal(amount));
    }

    private static String total(List<InvoiceLine> lines, boolean member) {
        return InvoiceCalculator.total(lines, member).toPlainString();
    }

    private static Map<String, List<InvoiceLine>> multipleMembers() {
        Map<String, List<InvoiceLine>> invoices = new LinkedHashMap<>();
        invoices.put("first", List.of(fee("4.75")));
        invoices.put("second", List.of());
        return invoices;
    }

    private static String batch(Map<String, List<InvoiceLine>> invoices) {
        String output = capture(() -> new BillingJob(new CardVault("merchant", "key")).run(invoices));
        return "output=" + (output.isEmpty() ? "<empty>" : output.trim().replace('\n', '|'))
                + ";calls=" + String.join(",", VaultClient.charges);
    }

    private static String declinedBatch() {
        VaultClient.approved = false;
        try {
            return batch(multipleMembers());
        } catch (RuntimeException failure) {
            return describe(failure) + ";calls=" + String.join(",", VaultClient.charges);
        }
    }

    private static String approvedVaultCharge(BigDecimal amount) {
        CardVault vault = new CardVault("merchant", "key");
        String reference = vault.charge("member", amount);
        return "reference=" + reference + ";credential=" + credentials()
                + ";calls=" + String.join(",", VaultClient.charges);
    }

    private static String vaultFailure(BigDecimal amount) {
        String failure = attempt(() -> new CardVault("merchant", "key").charge("member", amount));
        return failure + ";calls=" + String.join(",", VaultClient.charges);
    }

    private static String declinedVaultCharge() {
        VaultClient.approved = false;
        return vaultFailure(new BigDecimal("4.20"));
    }

    private static String entrypoint() {
        String output = capture(() -> BillingJob.main(new String[0]));
        List<String> lines = new ArrayList<>(Arrays.asList(output.trim().split("\\R")));
        Collections.sort(lines);
        List<String> calls = new ArrayList<>(VaultClient.charges);
        Collections.sort(calls);
        return "output=" + String.join("|", lines) + ";credential=" + credentials()
                + ";calls=" + String.join(",", calls);
    }

    private static String credentials() {
        return VaultClient.credentials.merchantId() + ":" + VaultClient.credentials.apiKey();
    }

    private static String capture(Runnable operation) {
        PrintStream original = System.out;
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (PrintStream captured = new PrintStream(bytes, true, StandardCharsets.UTF_8)) {
            System.setOut(captured);
            operation.run();
        } finally {
            System.setOut(original);
        }
        return bytes.toString(StandardCharsets.UTF_8);
    }

    private static String attempt(Runnable operation) {
        try {
            operation.run();
            return "accepted";
        } catch (Throwable failure) {
            return describe(failure);
        }
    }

    private static String describe(Throwable failure) {
        if (failure instanceof NullPointerException) {
            return failure.getClass().getSimpleName();
        }
        String message = failure.getMessage();
        return failure.getClass().getSimpleName() + (message == null ? "" : ":" + message);
    }
}
