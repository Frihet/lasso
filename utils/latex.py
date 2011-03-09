import tempfile
import subprocess
import django.http
import django.template.loader
import os.path
import shutil

def render_to_response(template, dct, context_instance):
    if 'request' in context_instance and context_instance['request'].GET.get('format', '') == 'tex':
        return django.http.HttpResponse(django.template.loader.render_to_string(template, dct, context_instance).encode('utf-8'), mimetype="text/plain")

    workdir = tempfile.mkdtemp()
    try:
        texfile = os.path.join(workdir, 'withdrawal_print.tex')
        with open(texfile, 'w') as f:
            f.write(django.template.loader.render_to_string(template, dct, context_instance).encode('utf-8'))

        try:
            subprocess.check_call(["pdflatex", "-interaction=batchmode", texfile], cwd=workdir)
        except:
            pass

        pdffile = os.path.join(workdir, 'withdrawal_print.pdf')
        with open(pdffile) as f:
            pdf = f.read()

        return django.http.HttpResponse(pdf, mimetype="application/pdf")
    finally:
        shutil.rmtree(workdir)
