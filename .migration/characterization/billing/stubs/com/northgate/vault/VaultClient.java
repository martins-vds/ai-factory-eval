package com.northgate.vault;

import java.util.ArrayList;
import java.util.List;

public final class VaultClient {
    public static VaultCredentials credentials;
    public static boolean approved = true;
    public static String reason = "insufficient funds";
    public static final List<String> charges = new ArrayList<>();

    public static VaultClient connect(VaultCredentials suppliedCredentials) {
        credentials = suppliedCredentials;
        return new VaultClient();
    }

    public ChargeResult charge(String memberId, long cents, String currency) {
        charges.add(memberId + ":" + cents + ":" + currency);
        return new ChargeResult(approved, "ref-" + memberId, reason);
    }

    public static void reset() {
        credentials = null;
        approved = true;
        reason = "insufficient funds";
        charges.clear();
    }
}
