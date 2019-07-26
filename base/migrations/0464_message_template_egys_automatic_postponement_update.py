# -*- coding: utf-8 -*-
# Generated by Laurent Spitaels on 2019-05-27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0463_auto_20190705_0841'),
    ]

    operations = [
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''{% autoescape off %}
                    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
                    <p>Bonjour,</p>
                    <p>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</p>
                    <p>Lancement de la proc&eacute;dure annuelle de copie des organisations de formation pour l&#39;ann&eacute;e acad&eacute;mique {{ current_academic_year }}.</p>
            
                    {% if egys_ending_this_year %}
                    <p><strong>{{ egys_ending_this_year }} OF avec une fin d&#39;enseignement en {{ current_academic_year }}.</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    {% if egys_already_existing %}
                    <p><strong>{{ egys_already_existing }} OF existant pr&eacute;alablement en {{ current_academic_year }}.</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    {% if egys_postponed %}
                    <p><strong>{{ egys_postponed }} OF copi&eacute;es de {{ previous_academic_year }} en {{ current_academic_year }}.</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for egy in egys_postponed_qs %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    {% if egys_with_errors %}
                    <p><strong>Les organisations de formation suivantes n&#39;ont pas &eacute;t&eacute; recopi&eacute;es :</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_with_errors %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    <p>Cordialement, Osis UCLouvain</p>
            {% endautoescape %}''',
               'egy_after_auto_postponement_html',
               'HTML',
               'fr-be'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''<p>Bonjour,</p>
                    
                    <p>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</p>
                    
                    <p>Lancement de la proc&eacute;dure annuelle de copie des organisations de formation pour l&#39;ann&eacute;e acad&eacute;mique {{ current_academic_year }}.</p>
                    
                    {% if egys_ending_this_year %}
                    <p><strong>{{ egys_ending_this_year }} OF avec une fin d&#39;enseignement en {{ current_academic_year }}.</strong></p>
                    
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    
                    {% if egys_already_existing %}
                    <p><strong>{{ egys_already_existing }} OF existant pr&eacute;alablement en {{ current_academic_year }}.</strong></p>
                    
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    
                    {% if egys_postponed %}
                    <p><strong>{{ egys_postponed }} OF copi&eacute;es de {{ previous_academic_year }} en {{ current_academic_year }}.</strong></p>
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for egy in egys_postponed_qs %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                        {% endfor %}
                    {% endif %}
                    
                    {% if egys_with_errors %}
                        <p><strong>Les organisations de formation suivantes n&#39;ont pas &eacute;t&eacute; recopi&eacute;es :</strong></p>
                    
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for eg in egys_with_errors %}
                        {% with egy=eg.educationgroupyear_set.last %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                         {% endwith %}
                        {% endfor %}
                    {% endif %}
                    <p>Cordialement, Osis UCLouvain</p>
                ''',
               'egy_after_auto_postponement_txt',
               'PLAIN',
               'fr-be'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''{% autoescape off %}
                    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
                    <p>Hello,</p>
                    <p>This is an automatic message generated by the OSIS server &ndash; Please do not reply to this message.</p>
                    <p>Report of the annual procedure of copy of the education groups for the academic year {{ current_academic_year }}.</p>
            
                    {% if egys_ending_this_year %}
                    <p><strong>{{ egys_ending_this_year }} EG ending in {{ current_academic_year }}.</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Acronym</th>
                                <th align="left">Code</th>
                                <th align="left">Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    {% if egys_already_existing %}
                    <p><strong>{{ egys_already_existing }} EG already existing in {{ current_academic_year }}.</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Acronym</th>
                                <th>Code</th>
                                <th>Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th>{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td>{{ egy.acronym|default:"" }}</td>
                                <td>{{ egy.partial_acronym|default:"" }}</td>
                                <td>{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    {% if egys_postponed %}
                    <p><strong>{{ egys_postponed }} EG copied from {{ previous_academic_year }} to {{ current_academic_year }}.</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Acronym</th>
                                <th>Code</th>
                                <th>Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for egy in egys_postponed_qs %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th>{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td>{{ egy.acronym|default:"" }}</td>
                                <td>{{ egy.partial_acronym|default:"" }}</td>
                                <td>{{ egy.complete_title }}</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
            
                    {% if egys_with_errors %}
                        <p><strong>Errors occured with the following education groups :</strong></p>
                        <div class="w3-responsive">
                        <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                            <thead>
                                <tr>
                                    <th>Acronym</th>
                                    <th>Code</th>
                                    <th>Title</th>
                                </tr>
                            </thead>
            
                            <tbody>
                            {% for eg in egys_with_errors %}
                                {% with egy=eg.educationgroupyear_set.last %}
                                <tr>
                                    <td>{{ egy.acronym|default:"" }}</td>
                                    <td>{{ egy.partial_acronym|default:"" }}</td>
                                    <td>{{ egy.complete_title }}</td>
                                </tr>
                                {% endwith %}
                            {% endfor %}
                            </tbody>
                        </table>
                        </div>
                    {% endif %}
            
                    <p>Regards, Osis UCLouvain</p>
            {% endautoescape %}''',
               'egy_after_auto_postponement_html',
               'HTML',
               'en'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''<p>Hello,</p>
                    
                    <p>This is an automatic message generated by the OSIS server &ndash; Please do not reply to this message.</p>
                    
                    <p>Report of the annual procedure of copy of the education groups for the academic year {{ current_academic_year }}.</p>
                    
                    {% if egys_ending_this_year %}
                    <p><strong>{{ egys_ending_this_year }} EG ending in {{ current_academic_year }}.</strong></p>
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    
                    {% if egys_already_existing %}
                    <p><strong>{{ egys_already_existing }} EG already existing in {{ current_academic_year }}.</strong></p>
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    
                    {% if egys_postponed %}
                    <p><strong>{{ egys_postponed }} EG copied from {{ previous_academic_year }} to {{ current_academic_year }}.</strong></p>
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for egy in egys_postponed_qs %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                        {% endfor %}
                    {% endif %}
                    
                    {% if egys_with_errors %}
                    
                        <p><strong>Errors occured with the following education groups :</strong></p>
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for eg in egys_with_errors %}
                        {% with egy=eg.educationgroupyear_set.last %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                        {% endwith %}
                        {% endfor %}
                    {% endif %}
                    
                    <p>Regards, Osis UCLouvain</p>
                ''',
               'egy_after_auto_postponement_txt',
               'PLAIN',
               'en'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET subject=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['Report of the annual procedure of copy of the education groups',
               'egy_after_auto_postponement_txt',
               'PLAIN',
               'en'])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET subject=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['Report of the annual procedure of copy of the education groups',
               'egy_after_auto_postponement_html',
               'HTML',
               'en'])],
        ),
    ]
