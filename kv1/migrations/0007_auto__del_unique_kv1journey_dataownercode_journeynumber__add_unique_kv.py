# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Kv1Journey', fields ['dataownercode', 'journeynumber']
        db.delete_unique(u'kv1_kv1journey', ['dataownercode', 'journeynumber'])

        # Adding unique constraint on 'Kv1Journey', fields ['dataownercode', 'line', 'journeynumber']
        db.create_unique(u'kv1_kv1journey', ['dataownercode', 'line_id', 'journeynumber'])


    def backwards(self, orm):
        # Removing unique constraint on 'Kv1Journey', fields ['dataownercode', 'line', 'journeynumber']
        db.delete_unique(u'kv1_kv1journey', ['dataownercode', 'line_id', 'journeynumber'])

        # Adding unique constraint on 'Kv1Journey', fields ['dataownercode', 'journeynumber']
        db.create_unique(u'kv1_kv1journey', ['dataownercode', 'journeynumber'])


    models = {
        u'kv1.kv1journey': {
            'Meta': {'unique_together': "(('dataownercode', 'line', 'journeynumber'),)", 'object_name': 'Kv1Journey'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journeynumber': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '6'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Line']"}),
            'stops': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['kv1.Kv1Stop']", 'through': u"orm['kv1.Kv1JourneyStop']", 'symmetrical': 'False'})
        },
        u'kv1.kv1journeydate': {
            'Meta': {'unique_together': "(('journey', 'date'),)", 'object_name': 'Kv1JourneyDate'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dates'", 'to': u"orm['kv1.Kv1Journey']"})
        },
        u'kv1.kv1journeystop': {
            'Meta': {'unique_together': "(('journey', 'stop'), ('journey', 'stoporder'))", 'object_name': 'Kv1JourneyStop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Journey']"}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kv1.Kv1Stop']"}),
            'stoporder': ('django.db.models.fields.SmallIntegerField', [], {}),
            'stoptype': ('django.db.models.fields.CharField', [], {'default': "'INTERMEDIATE'", 'max_length': '12'}),
            'targetarrival': ('django.db.models.fields.TimeField', [], {}),
            'targetdeparture': ('django.db.models.fields.TimeField', [], {})
        },
        u'kv1.kv1line': {
            'Meta': {'unique_together': "(('dataownercode', 'lineplanningnumber'),)", 'object_name': 'Kv1Line'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'headsign': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lineplanningnumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'publiclinenumber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'stop_map': ('json_field.fields.JSONField', [], {'default': "u'null'"})
        },
        u'kv1.kv1stop': {
            'Meta': {'unique_together': "(('dataownercode', 'userstopcode'),)", 'object_name': 'Kv1Stop'},
            'dataownercode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'userstopcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['kv1']