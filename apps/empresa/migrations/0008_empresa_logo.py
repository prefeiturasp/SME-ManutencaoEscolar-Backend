import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0007_alter_anexoresponsaveltecnico_arquivo_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="empresa",
            name="logo",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="empresas/logos/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=("png", "jpg", "jpeg"),
                        message="A logo deve ser um arquivo PNG, JPG ou JPEG.",
                    )
                ],
            ),
        ),
    ]
