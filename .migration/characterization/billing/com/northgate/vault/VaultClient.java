package com.northgate.vault;

import java.math.BigDecimal;

public final class VaultClient {
    private static boolean approved = true;
    private static String reason = "approved";
    private static String reference = "ref-standin";
    private static VaultCredentials credentials;
    private static String lastMemberId;
    private static long lastMinorUnits;
    private static String lastCurrency;

    private VaultClient() {
    }

    public static VaultClient connect(VaultCredentials suppliedCredentials) {
        credentials = suppliedCredentials;
        return new VaultClient();
    }

    public static void approve(String nextReference) {
        approved = true;
        reason = "approved";
        reference = nextReference;
    }

    public static void decline(String nextReason) {
        approved = false;
        reason = nextReason;
        reference = null;
    }

    public static void reset() {
        approved = true;
        reason = "approved";
        reference = "ref-standin";
        credentials = null;
        lastMemberId = null;
        lastMinorUnits = 0;
        lastCurrency = null;
    }

    public ChargeResult charge(String memberId, long minorUnits, String currency) {
        lastMemberId = memberId;
        lastMinorUnits = minorUnits;
        lastCurrency = currency;
        return new ChargeResult(approved, reason, reference);
    }

    public static VaultCredentials credentials() {
        return credentials;
    }

    public static String lastMemberId() {
        return lastMemberId;
    }

    public static long lastMinorUnits() {
        return lastMinorUnits;
    }

    public static String lastCurrency() {
        return lastCurrency;
    }
}
