#!/usr/bin/env bash
set -euo pipefail

repo=/home/runner/work/ai-factory-eval/ai-factory-eval
base="$repo/.migration/characterization/billing"
source="$repo/legacy-billing"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

cp -a "$source" "$scratch/legacy-billing"
set +e
(
  cd "$scratch/legacy-billing"
  mvn -q -B -DskipTests package
) >"$scratch/maven.log" 2>&1
maven_status=$?
set -e
printf 'TIER-B BUILD ATTEMPT: mvn -q -B -DskipTests package exit=%d\n' "$maven_status"
if [ "$maven_status" -ne 0 ]; then
  sed -n '/Could not find artifact/ p;/Could not resolve dependencies/ p;/repositories/ p' "$scratch/maven.log" | head -20
fi

mkdir -p "$scratch/classes"
javac -d "$scratch/classes" \
  "$base/com/northgate/vault/ChargeResult.java" \
  "$base/com/northgate/vault/VaultCredentials.java" \
  "$base/com/northgate/vault/VaultClient.java" \
  "$source/src/main/java/billing/InvoiceLine.java" \
  "$source/src/main/java/billing/InvoiceCalculator.java" \
  "$source/src/main/java/billing/CardVault.java" \
  "$source/src/main/java/billing/BillingJob.java" \
  "$base/BillingCharacterization.java"

NORTHGATE_MERCHANT=characterization-merchant \
NORTHGATE_KEY=characterization-key \
java -cp "$scratch/classes" billing.BillingCharacterization
