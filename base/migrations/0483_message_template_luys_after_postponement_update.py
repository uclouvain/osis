# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-31 13:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0482_message_template_luys_automatic_postponement_update'),
    ]

    operations = [
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
             ['''{% autoescape off %}
             <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
             <p>Bonjour,</p>
             <p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>
             <p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des unit\u00e9s d\u0027enseignement pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>
            
             <p>{{ luys_ending_this_year }} UE avec une fin d\u0027enseignement en {{ academic_year }}.</p>
             {% if luys_ending_this_year %}    
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             
             <p><strong>{{ luys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}          
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_already_existing_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             
             <p>{{ luys_postponed }} UE copi\u00e9es de {{ academic_year }} en {{ end_academic_year }}.</p>
             {% if luys_postponed %}
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for luy in luys_postponed_qs %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             
             {% if luys_with_errors %}
             <p>Les unit\u00e9s d\u0027enseignement suivantes n\u0027ont pas \u00e9t\u00e9 recopi\u00e9es :</p>
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_with_errors %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             <p>Cordialement, Osis UCLouvain</p>
             {% endautoescape %}''',
              'luy_after_auto_postponement_html',
              'HTML',
              'fr-be'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
             ['''<p>Bonjour,</p>
             <p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>
             <p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des unit\u00e9s d\u0027enseignement pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>
             
             <p>{{ luys_ending_this_year }} UE avec une fin d\u0027enseignement en {{ academic_year }}.</p>
             {% if luys_ending_this_year %}                    
             <strong>Code - Intitul&eacute;</strong><br/>
                 {% for lu in luyss_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                 {% endfor %}
             {% endif %}
                    
             <p><strong>{{ luys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}                
                <strong>Code - Intitul&eacute;</strong><br/>
                    {% for lu in luys_ending_this_year_qs %}
                        {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                        {% endwith %}
                    {% endfor %}
             {% endif %}
             
             <p>{{ luys_postponed }} UE copi\u00e9es de {{ academic_year }} en {{ end_academic_year }}.</p>
             {% if luys_postponed %}
             <strong>Code - Intitul&eacute;</strong><br/>
                 {% for luy in luys_postponed_qs %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                 {% endfor %}
             {% endif %}                       
             
             {% if luys_with_errors %}
                 <p>Les unit\u00e9s d\u0027enseignement suivantes n\u0027ont pas \u00e9t\u00e9 recopi\u00e9es :</p>
                 strong>Code - Intitul&eacute;</strong><br/>
                    {% for lu in luys_with_errors %}
                    {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                    {% endfor %}
             {% endif %}
             
             <p>Cordialement, Osis UCLouvain</p>
             ''',
              'luy_after_auto_postponement_txt',
              'PLAIN',
              'fr-be'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
             ['''{% autoescape off %}
             <p>Hello,</p>
             <p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>
             <p>Report of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>
             
             <p>{{ luys_ending_this_year }} LU ending in {{ academic_year }}.</p>
             {% if luys_ending_this_year %}                    
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
                    
             <p><strong>{{ luys_already_existing }} LU already existing in {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}                
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_already_existing_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             
             <p>{ luys_postponed }} LU copied from {{ academic_year }} to {{ end_academic_year }}.</p>
             {% if luys_postponed %}
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for luy in luys_postponed_qs %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}                  
             
             {% if luys_with_errors %}
             <p>Errors occured with the following learning units :</p>
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_with_errors %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             
             <p>Regards, Osis UCLouvain</p>
             {% endautoescape off %}''',
              'luy_after_auto_postponement_html',
              'HTML',
              'en'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
             ['''<p>Hello,</p>
             <p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>
             <p>Report of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>
             
             <p>{{ luys_ending_this_year }} LU ending in {{ academic_year }}.</p>
             {% if luys_ending_this_year %}                    
             <strong>Code - Title</strong><br/>
                 {% for lu in luyss_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                 {% endfor %}
             {% endif %}
                    
             <p><strong>{{ luys_already_existing }} LU already existing in {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}                
                <strong>Code - Title</strong><br/>
                    {% for lu in luys_ending_this_year_qs %}
                        {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                        {% endwith %}
                    {% endfor %}
             {% endif %}
             
             <p>{ luys_postponed }} LU copied from {{ academic_year }} to {{ end_academic_year }}.</p>
             {% if luys_postponed %}
             <strong>Code - Title</strong><br/>
                 {% for luy in luys_postponed_qs %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                 {% endfor %}
             {% endif %}                             
             
             {% if luys_with_errors %}
                 <p>Errors occured with the following learning units :</p>
                 strong>Code - Title</strong><br/>
                    {% for lu in luys_with_errors %}
                    {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                    {% endfor %}
             {% endif %}
             
             <p>Regards, Osis UCLouvain</p>
             ''',
              'luy_after_auto_postponement_txt',
              'PLAIN',
              'en'])],
        ),
    ]