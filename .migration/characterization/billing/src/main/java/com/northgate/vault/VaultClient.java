package com.northgate.vault;

import java.util.ArrayList;
import java.util.List;

public final class VaultClient {
    private static final List<Charge> CHARGES = new ArrayList<>();
    private static VaultCredentials credentials;
    private static boolean approved = true;
    private static String declineReason = "insufficient funds";

    private VaultClient() {
    }

    public static VaultClient connect(VaultCredentials suppliedCredentials) {
        credentials = suppliedCredentials;
        requireExpectedCredential("billing.expectedMerchant", suppliedCredentials.merchantId());
        requireExpectedCredential("billing.expectedKey", suppliedCredentials.apiKey());
        return new VaultClient();
    }

    public ChargeResult charge(String memberId, long amountCents, String currency) {
        CHARGES.add(new Charge(memberId, amountCents, currency));
        return new ChargeResult(approved, "ref-" + memberId, declineReason);
    }

    public static void reset() {
        CHARGES.clear();
        credentials = null;
        approved = true;
        declineReason = "insufficient funds";
    }

    public static void declineWith(String reason) {
        approved = false;
        declineReason = reason;
    }

    public static List<Charge> charges() {
        return List.copyOf(CHARGES);
    }

    public static VaultCredentials credentials() {
        return credentials;
    }

    private static void requireExpectedCredential(String property, String actual) {
        String expected = System.getProperty(property);
        if (expected != null && !expected.equals(actual)) {
            throw new IllegalStateException("unexpected credential: " + property);
        }
    }

    public record Charge(String memberId, long amountCents, String currency) {
    }
}
