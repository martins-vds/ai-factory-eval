package com.northgate.vault;

public final class VaultCredentials {
    private final String merchantId;
    private final String apiKey;

    public VaultCredentials(String merchantId, String apiKey) {
        this.merchantId = merchantId;
        this.apiKey = apiKey;
    }

    public String merchantId() {
        return merchantId;
    }

    public String apiKey() {
        return apiKey;
    }
}
