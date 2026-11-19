import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SUITE = Path(__file__).resolve().parent
SOURCE = ROOT / "legacy-billing" / "src" / "main" / "java"


class BillingCharacterization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classes = tempfile.TemporaryDirectory(prefix="billing-characterization-")
        java_sources = [
            SOURCE / "billing" / name
            for name in ("InvoiceLine.java", "InvoiceCalculator.java", "CardVault.java", "BillingJob.java")
        ]
        java_sources.extend(sorted((SUITE / "stubs").rglob("*.java")))
        java_sources.append(SUITE / "src" / "billing" / "CharacterizationHarness.java")
        subprocess.run(
            ["javac", "-encoding", "UTF-8", "--release", "17", "-d", cls.classes.name, *map(str, java_sources)],
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.classes.cleanup()

    def observe(self, scenario):
        environment = os.environ.copy()
        environment.update(
            NORTHGATE_MERCHANT="characterization-merchant",
            NORTHGATE_KEY="characterization-key",
        )
        result = subprocess.run(
            ["java", "-cp", self.classes.name, "billing.CharacterizationHarness", scenario],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        return result.stdout

    def assert_observed(self, scenario, expected):
        self.assertEqual(expected, self.observe(scenario))

    def test_invoice_line_accepts_zero(self):
        self.assert_observed("line-zero", "0.00")

    def test_invoice_line_rejects_negative_amount(self):
        self.assert_observed("line-negative", "IllegalArgumentException:negative charge: late")

    def test_invoice_line_null_amount_fails(self):
        self.assert_observed("line-null", "NullPointerException")

    def test_member_invoice_total(self):
        self.assert_observed("total-member", "8.14")

    def test_late_fees_are_capped_before_monthly_fee_and_tax(self):
        self.assert_observed("total-cap", "29.40")

    def test_nonmember_invoice_total(self):
        self.assert_observed("total-nonmember", "2.10")

    def test_tax_rounds_half_up_once(self):
        self.assert_observed("total-half-up", "0.53")

    def test_empty_member_invoice_includes_monthly_fee_and_tax(self):
        self.assert_observed("total-empty-member", "3.15")

    def test_empty_nonmember_invoice_is_zero(self):
        self.assert_observed("total-empty-nonmember", "0.00")

    def test_null_fee_list_fails(self):
        self.assert_observed("total-null-list", "NullPointerException")

    def test_null_fee_line_fails(self):
        self.assert_observed("total-null-line", "NullPointerException")

    def test_amount_below_one_dollar_is_not_chargeable(self):
        self.assert_observed("charge-below", "false")

    def test_amount_at_one_dollar_is_chargeable(self):
        self.assert_observed("charge-boundary", "true")

    def test_null_total_fails(self):
        self.assert_observed("charge-null", "NullPointerException")

    def test_empty_batch_has_no_output_or_charges(self):
        self.assert_observed("batch-empty", "output=<empty>;calls=")

    def test_empty_member_invoice_is_charged(self):
        self.assert_observed(
            "batch-member-empty",
            "output=member charged 3.15 ref ref-member;calls=member:315:USD",
        )

    def test_batch_charges_each_member_and_reports_references(self):
        self.assert_observed(
            "batch-multiple",
            "output=first charged 8.14 ref ref-first|second charged 3.15 ref ref-second"
            ";calls=first:814:USD,second:315:USD",
        )

    def test_declined_charge_stops_batch(self):
        self.assert_observed(
            "batch-decline",
            "IllegalStateException:card declined for first: insufficient funds;calls=first:814:USD",
        )

    def test_null_batch_fails(self):
        self.assert_observed("batch-null-map", "NullPointerException")

    def test_null_member_fees_fail(self):
        self.assert_observed("batch-null-fees", "NullPointerException")

    def test_vault_converts_approved_charge_to_cents_and_returns_reference(self):
        self.assert_observed(
            "vault-approved",
            "reference=ref-member;credential=merchant:key;calls=member:814:USD",
        )

    def test_vault_passes_zero_amount_as_zero_cents(self):
        self.assert_observed(
            "vault-zero",
            "reference=ref-member;credential=merchant:key;calls=member:0:USD",
        )

    def test_vault_passes_negative_amount_as_negative_cents(self):
        self.assert_observed(
            "vault-negative",
            "reference=ref-member;credential=merchant:key;calls=member:-100:USD",
        )

    def test_vault_rejects_fractional_cent_without_calling_provider(self):
        self.assert_observed("vault-fraction", "ArithmeticException:Rounding necessary;calls=")

    def test_vault_null_amount_fails_without_calling_provider(self):
        self.assert_observed("vault-null", "NullPointerException;calls=")

    def test_vault_decline_throws_provider_reason(self):
        self.assert_observed(
            "vault-decline",
            "IllegalStateException:card declined for member: insufficient funds;calls=member:420:USD",
        )

    def test_entrypoint_reads_credentials_and_bills_fixed_members(self):
        self.assert_observed(
            "entrypoint",
            "output=ana charged 8.14 ref ref-ana|ben charged 3.15 ref ref-ben"
            ";credential=characterization-merchant:characterization-key"
            ";calls=ana:814:USD,ben:315:USD",
        )

    def test_launcher_runs_maven_then_java_with_target_dependency_classpath(self):
        with tempfile.TemporaryDirectory(prefix="billing-launcher-") as temporary:
            bin_dir = Path(temporary) / "bin"
            bin_dir.mkdir()
            log = Path(temporary) / "calls.log"
            for executable in ("mvn", "java"):
                script = bin_dir / executable
                script.write_text(
                    "#!/bin/sh\n"
                    f'printf "%s\\n" "{executable} $*" >> "$LAUNCH_LOG"\n',
                    encoding="utf-8",
                )
                script.chmod(0o755)
            environment = os.environ.copy()
            environment.update(PATH=f"{bin_dir}:{environment['PATH']}", LAUNCH_LOG=str(log))
            subprocess.run(
                ["bash", str(ROOT / "legacy-billing" / "run.sh")],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(
                "mvn -q -B package\njava -cp target/classes:target/dependency/* billing.BillingJob\n",
                log.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
