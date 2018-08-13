# Generated by Django 2.0.2 on 2018-04-14 18:19

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('building_code', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('campus', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number', models.CharField(max_length=6)),
                ('title', models.CharField(max_length=100)),
                ('multiple_offerings', models.BooleanField()),
                ('academic_credits', models.CharField(blank=True, max_length=25, null=True)),
                ('academic_career', models.CharField(blank=True, max_length=50, null=True)),
                ('academic_group', models.CharField(blank=True, max_length=50, null=True)),
                ('prerequisites', models.TextField(blank=True, null=True)),
                ('description', models.TextField(default='No description found.')),
                ('attributes', models.TextField(blank=True, null=True)),
                ('expanded_id', models.CharField(default=None, max_length=25, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('letter', models.CharField(max_length=1, primary_key=True, serialize=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150)),
                ('title', models.CharField(blank=True, default=None, max_length=100)),
                ('internal_id', models.CharField(blank=True, default=None, max_length=50, unique=True)),
                ('email', models.EmailField(blank=True, default=None, max_length=254, unique=True)),
                ('six_plus_two', models.CharField(blank=True, default=None, max_length=8, unique=True)),
                ('search_first_name', models.CharField(blank=True, default=None, max_length=75)),
                ('search_last_name', models.CharField(blank=True, default=None, max_length=75)),
                ('office_phone_number', models.CharField(max_length=15, null=True)),
                ('office_number', models.CharField(max_length=25, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('short_name', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('long_name', models.CharField(max_length=50)),
                ('last_scraped', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('code', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('season', models.CharField(choices=[('Spring', 'Spring'), ('Summer', 'Summer'), ('Fall', 'Fall')], max_length=6)),
                ('year', models.PositiveSmallIntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='TopLevelCatalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short', models.CharField(max_length=25)),
                ('long', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=25)),
                ('expanded_id', models.CharField(max_length=25)),
                ('title', models.CharField(max_length=255)),
                ('multiple_offerings', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'TLC Entry',
                'verbose_name_plural': 'TLC Entries',
            },
        ),
        migrations.AlterUniqueTogether(
            name='toplevelcatalog',
            unique_together={('short', 'number')},
        ),
        migrations.AddField(
            model_name='course',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bearcatalog.Subject'),
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('subject', 'number')},
        ),
    ]
