# coding: utf-8
import hues
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from elasticsearch_dsl.connections import connections
from elasticsearch_flex.indexes import registered_indices


class Command(BaseCommand):
    help = 'Setup Search Index'

    def handle(self, *args, **options):
        indices = registered_indices()
        connection = connections.get_connection()
        hues.info('Using connection', connection)
        if len(indices):
            hues.info('Discovered', len(indices), 'Indexes')
        else:
            hues.warn('No search indexe found')
        for i, index in enumerate(indices, 1):
            hues.info('==> Initializing', index)
            index_name = index._doc_type.index
            connection.indices.close(index_name)
            index.init()
            connection.indices.open(index_name)
            hues.info('--> Indexing from', index.model)
            for obj in tqdm(index.queryset):
                doc = index.init_using_pk(obj.pk)
                doc.prepare()
                doc.save()
            hues.success('--> {0}/{1} indexed.'.format(i, len(indices)))
