"""Quote-verifier regression checks; no model/server/database access."""
import unittest
from experiments.local_ai.personal_review_probe import audit_quotes


class QuoteAuditTests(unittest.TestCase):
    def findings(self,quote):
        return {'criteria_findings':[{'criterion_index':i,'quotes':[quote] if i==0 else []}
                                     for i in range(4)]}

    def test_verbatim_quote_passes_but_reworded_case_changed_or_joined_quote_does_not(self):
        source='A transaction groups both updates. Rollback undoes changes if either fails.'
        for quote,expected in [('Rollback undoes changes',True),
                               ('rollback undoes changes',False),
                               ('Rollback reverses changes',False),
                               ('groups both updates ... if either fails',False),
                               ('Rollback cancels the transaction.',False)]:
            with self.subTest(quote=quote):
                self.assertEqual(audit_quotes(self.findings(quote),source)['checks'][0]['exact_substring'],expected)

    def test_missing_quotes_or_bad_criterion_indices_do_not_create_semantic_certification(self):
        output=self.findings('');report=audit_quotes(output,'source')
        self.assertFalse(report['checks'][0]['exact_substring'])
        output['criteria_findings'][3]['criterion_index']=0
        self.assertFalse(audit_quotes(output,'source')['criterion_indices_valid'])
        self.assertNotIn('conclusion_supported',report)


if __name__=='__main__':unittest.main()
