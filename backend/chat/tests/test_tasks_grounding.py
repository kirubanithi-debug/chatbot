from django.test import SimpleTestCase

from chat.tasks import normalize_ai_response


class ResponseGroundingTests(SimpleTestCase):
    def test_grounding_overrides_wrong_law_and_punishment(self):
        entry = {
            'law': 'IPC 379',
            'section': 'Punishment for theft',
            'punishment': 'Up to 3 years imprisonment, or fine, or both',
            'next_steps': '1. File FIR. 2. Preserve evidence. 3. Follow-up.',
            'keywords': 'theft stolen bike',
        }
        ai_response = (
            'LAW: IPC 420\n'
            'SECTION: Cheating\n'
            'PUNISHMENT: 7 years\n'
            'NEXT STEPS: 1. Report to cyber cell. 2. Share screenshots. 3. Contact bank.\n'
            'DISCLAIMER: Consult lawyer'
        )

        output = normalize_ai_response(ai_response=ai_response, entry=entry)

        self.assertIn('LAW: IPC 379', output)
        self.assertIn('SECTION: Punishment for theft', output)
        self.assertIn('PUNISHMENT: Up to 3 years imprisonment, or fine, or both', output)
        self.assertIn('NEXT STEPS: 1. Report to cyber cell. 2. Share screenshots. 3. Contact bank.', output)

    def test_grounding_uses_entry_next_steps_when_ai_placeholder(self):
        entry = {
            'law': 'IPC 379',
            'section': 'Punishment for theft',
            'punishment': 'Up to 3 years imprisonment, or fine, or both',
            'next_steps': '1. File FIR. 2. Preserve evidence. 3. Follow-up.',
            'keywords': 'theft',
        }
        ai_response = (
            'LAW: IPC 420\n'
            'SECTION: Cheating\n'
            'PUNISHMENT: 7 years\n'
            'NEXT STEPS: Consult lawyer\n'
            'DISCLAIMER: Consult lawyer'
        )

        output = normalize_ai_response(ai_response=ai_response, entry=entry)

        self.assertIn('LAW: IPC 379', output)
        self.assertIn('SECTION: Punishment for theft', output)
        self.assertIn('NEXT STEPS: 1. File FIR. 2. Preserve evidence. 3. Follow-up.', output)

    def test_context_first_document_is_used_as_trusted_entry(self):
        context = (
            'LAW: IPC 379\n'
            'SECTION: Punishment for theft\n'
            'PUNISHMENT: Up to 3 years imprisonment\n'
            'NEXT STEPS: 1. File FIR.\n\n'
            'LAW: IPC 420\n'
            'SECTION: Cheating\n'
            'PUNISHMENT: Up to 7 years imprisonment\n'
            'NEXT STEPS: 1. Cyber complaint.'
        )
        ai_response = (
            'LAW: IPC 420\n'
            'SECTION: Cheating\n'
            'PUNISHMENT: Up to 7 years imprisonment\n'
            'NEXT STEPS: 1. Anything\n'
            'DISCLAIMER: Consult lawyer'
        )

        output = normalize_ai_response(ai_response=ai_response, context=context)

        self.assertIn('LAW: IPC 379', output)
        self.assertIn('SECTION: Punishment for theft', output)
        self.assertIn('PUNISHMENT: Up to 3 years imprisonment', output)
