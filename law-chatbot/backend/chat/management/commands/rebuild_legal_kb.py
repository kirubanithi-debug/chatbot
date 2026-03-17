from django.core.management.base import BaseCommand

from chat.rag_setup import clear_runtime_caches, rebuild_knowledge_base


class Command(BaseCommand):
    help = 'Rebuilds legal knowledge base (CSV -> Chroma vector store) and clears in-memory caches.'

    def handle(self, *args, **options):
        self.stdout.write('Rebuilding legal knowledge base...')
        try:
            rebuild_knowledge_base()
            self.stdout.write(self.style.SUCCESS('Legal knowledge base rebuilt successfully.'))
        except Exception as exc:
            # Keep runtime usable through keyword fallback even if vector DB rebuild fails.
            clear_runtime_caches()
            self.stderr.write(self.style.WARNING(f'Vector store rebuild failed: {exc}'))
            self.stdout.write(self.style.SUCCESS('Caches refreshed. Keyword-based retrieval remains available.'))
