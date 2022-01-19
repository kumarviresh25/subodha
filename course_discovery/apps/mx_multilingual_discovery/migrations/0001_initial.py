# Generated by Django 2.2.16 on 2022-01-11 09:04

from django.db import migrations, models
import django.db.models.deletion
import parler.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course_metadata', '0258_delete_programtranslation'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiLingualDiscovery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('program', 'Program'), ('course', 'Course'), ('tag', 'Tag')], max_length=20, verbose_name='Content Type')),
                ('course_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multilingual_course', to='course_metadata.CourseRun', verbose_name='Course Key')),
                ('program_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multilingual_program', to='course_metadata.Program', verbose_name='Program Key')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='MultiLingualDiscoveryTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('short_descriprion', models.CharField(blank=True, max_length=255, null=True, verbose_name='Short Description')),
                ('full_descriprion', models.TextField(blank=True, null=True, verbose_name='Full Description')),
                ('master', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discovery_translations', to='mx_multilingual_discovery.MultiLingualDiscovery')),
            ],
            options={
                'abstract': False,
                'default_permissions': (),
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
