package com.northgate.vault;

import java.util.ArrayList;
import java.util.List;

public final class VaultClient {
    private static VaultCredentials connectedCredentials;
    private static ChargeResult result;
    private static final List<Charge> charges = new ArrayList<>();

    private VaultClient() {
    }

    public static VaultClient connect(VaultCredentials credentials) {
        connectedCredentials = credentials;
        return new VaultClient();
    }

    public ChargeResult charge(String memberId, long cents, String currency) {
        charges.add(new Charge(memberId, cents, currency));
        return result;
    }

    public static void reset() {
        connectedCredentials = null;
        result = new ChargeResult(true, "", "test-reference");
        charges.clear();
    }

    public static void setResult(ChargeResult nextResult) {
        result = nextResult;
    }

    public static VaultCredentials connectedCredentials() {
        return connectedCredentials;
    }

    public static List<Charge> charges() {
        return List.copyOf(charges);
    }

    public record Charge(String memberId, long cents, String currency) {
    }
}
