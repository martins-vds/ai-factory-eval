package com.northgate.vault;

public final class VaultClient {
    public static VaultCredentials lastCredentials;
    public static String lastMemberId;
    public static long lastAmount;
    public static String lastCurrency;
    public static boolean approved;
    public static String reason;
    public static String reference;

    public static VaultClient connect(VaultCredentials credentials) {
        lastCredentials = credentials;
        return new VaultClient();
    }

    public ChargeResult charge(String memberId, long amount, String currency) {
        lastMemberId = memberId;
        lastAmount = amount;
        lastCurrency = currency;
        return new ChargeResult(approved, reason, reference);
    }

    public static void reset() {
        lastCredentials = null;
        lastMemberId = null;
        lastAmount = 0;
        lastCurrency = null;
        approved = true;
        reason = "declined";
        reference = "approved-reference";
    }
}
