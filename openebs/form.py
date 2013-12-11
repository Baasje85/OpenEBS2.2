from crispy_forms.bootstrap import AccordionGroup, Accordion, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML, Div, Hidden
from django.utils.timezone import now
import floppyforms as forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from kv1.models import Kv1Stop, Kv1Line, Kv1Journey
from kv15.enum import REASONTYPE, SUBREASONTYPE, ADVICETYPE, SUBADVICETYPE
from models import Kv15Stopmessage, Kv15Scenario, Kv15ScenarioMessage, get_end_service, Kv17Change
from openebs.models import Kv17JourneyChange


class Kv15StopMessageForm(forms.ModelForm):
    def clean(self):
        # TODO Move _all_ halte parsing here!
        ids = []
        for halte in self.data['haltes'].split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    ids.append(stop.pk)
                else:
                    raise ValidationError(_("Datafout: halte niet gevonden in database. Meld dit bij een beheerder."))
                    break
        if len(ids) == 0:
            raise ValidationError(_("Selecteer minimaal een halte"))
        else:
            return self.cleaned_data

    class Meta:
        model = Kv15Stopmessage
        exclude = ['messagecodenumber', 'status', 'stops', 'messagecodedate', 'isdeleted', 'id', 'dataownercode', 'user']
        widgets = {
            'messagecontent': forms.Textarea(attrs={'cols' : 50, 'rows' : 6, 'class' : 'col-lg-6', 'maxlength':255 }),
            'reasoncontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority' : forms.RadioSelect,
            'messagedurationtype' : forms.RadioSelect,
            'messagetype' : forms.RadioSelect,
            'messagestarttime' : forms.DateTimeInput,
            'messageendtime' : forms.DateTimeInput,
            'reasontype' : forms.RadioSelect,
            'subreasontype' : forms.Select,
            'effecttype' : forms.RadioSelect,
            'subeffecttype' : forms.Select,
            'measuretype' : forms.RadioSelect,
            'submeasuretype' : forms.Select,
            'advicetype' : forms.RadioSelect,
            'subadvicetype' : forms.Select,
            'messagetimestamp' : forms.DateTimeInput
        }


    def __init__(self, *args, **kwargs):
        super(Kv15StopMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(HTML('<span class="charcount badge badge-success pull-right">0</span>'),
                Field('messagecontent'),  css_class='countwrapper'),
                'messagestarttime',
                'messageendtime',
            Accordion(
                AccordionGroup(_('Bericht instellingen'),
                    'messagepriority',
                    'messagetype',
                    'messagedurationtype'
                ),
                AccordionGroup(_('Oorzaak'),
                   'reasontype',
                   'subreasontype',
                   'reasoncontent'
                ),
                AccordionGroup(_('Effect'),
                   'effecttype',
                   'subeffecttype',
                   'effectcontent'
                ),
                AccordionGroup(_('Gevolg'),
                   'measuretype',
                   'submeasuretype',
                   'measurecontent'
                ),
                AccordionGroup(_('Advies'),
                   'advicetype',
                   'subadvicetype',
                   'advicecontent'
                )
            )
        )

class Kv15ScenarioForm(forms.ModelForm):
    class Meta:
        model = Kv15Scenario
        exclude = ['dataownercode']
        widgets = {
            'description': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
        }

    def __init__(self, *args, **kwargs):
        super(Kv15ScenarioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form_horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'


class Kv15ScenarioMessageForm(forms.ModelForm):

    def clean(self):
        # TODO Move _all_ halte parsing here!
        ids = []
        for halte in self.data['haltes'].split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    ids.append(stop.pk)
        qry = Kv1Stop.objects.filter(kv15scenariostop__message__scenario=self.data['scenario'], pk__in=ids)
        if self.instance.pk is not None: # Exclude ourselves if we've been saved
            qry = qry.exclude(kv15scenariostop__message=self.instance.pk)

        if qry.count() > 0:
            # Check that this stop isn't already in a messages for this scenario
            out = ""
            for stop in qry:
                out += "%s, " % stop.name
            raise ValidationError(_("Halte(s) ' %s ' bestaan al voor dit scenario") % out)
        elif len(ids) == 0:
            # Select at least one stop for a message
            raise ValidationError(_("Selecteer minimaal een halte"))
        else:
            return self.cleaned_data

    class Meta:
        model = Kv15ScenarioMessage
        exclude = ['dataownercode']
        widgets = {
            'scenario': forms.HiddenInput,
            'messagecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'reasoncontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'effectcontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'measurecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),
            'advicecontent': forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}),

            # This is awful, but is neccesary because otherwise we don't get nice bootstrappy widgets
            'messagepriority' : forms.RadioSelect,
            'messagetype' : forms.RadioSelect,
            'messagedurationtype' : forms.RadioSelect,
            'messagestarttime' : forms.DateTimeInput,
            'messageendtime' : forms.DateTimeInput,
            'reasontype' : forms.RadioSelect,
            'subreasontype' : forms.Select,
            'effecttype' : forms.RadioSelect,
            'subeffecttype' : forms.Select,
            'measuretype' : forms.RadioSelect,
            'submeasuretype' : forms.Select,
            'advicetype' : forms.RadioSelect,
            'subadvicetype' : forms.Select
        }

    def __init__(self, *args, **kwargs):
        super(Kv15ScenarioMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'scenario',
            'messagecontent',
            Accordion(
                AccordionGroup(_('Bericht instellingen'),
                    'messagepriority',
                    'messagetype',
                    'messagedurationtype'
                ),
                AccordionGroup(_('Oorzaak'),
                   'reasontype',
                   'subreasontype',
                   'reasoncontent'
                ),
                AccordionGroup(_('Effect'),
                   'effecttype',
                   'subeffecttype',
                   'effectcontent'
                ),
                AccordionGroup(_('Gevolg'),
                   'measuretype',
                   'submeasuretype',
                   'measurecontent'
                ),
                AccordionGroup(_('Advies'),
                   'advicetype',
                   'subadvicetype',
                   'advicecontent'
                )
            )
        )

class Kv17ChangeForm(forms.ModelForm):
    # This is duplication, but should work
    reasontype = forms.ChoiceField(choices=REASONTYPE, label=_("Type oorzaak"), required=False)
    subreasontype = forms.ChoiceField(choices=SUBREASONTYPE, label=_("Oorzaak"), required=False)
    reasoncontent = forms.CharField(max_length=255, label=_("Uitleg oorzaak"), required=False,
                                    widget=forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}))
    advicetype = forms.ChoiceField(choices=ADVICETYPE, label=_("Type advies"), required=False)
    subadvicetype = forms.ChoiceField(choices=SUBADVICETYPE, label=_("Advies"), required=False)
    advicecontent = forms.CharField(max_length=255, label=_("Uitleg advies"), required=False,
                                    widget=forms.Textarea(attrs={'cols' : 40, 'rows' : 4, 'class' : 'col-lg-6'}))

    def clean(self):
        cleaned_data = super(Kv17ChangeForm, self).clean()
        cleaned_data['dataownercode'] = cleaned_data['line'].dataownercode
        if Kv17Change.objects.filter(operatingday=now(), line=cleaned_data['line'],
                                     journey=cleaned_data['journey']).count() != 0:
            raise ValidationError(_("Deze rit is al aangepast, selecteer een andere rit"))
        if cleaned_data['line'] != cleaned_data['journey'].line \
            or cleaned_data['line'].dataownercode != cleaned_data['journey'].dataownercode:
            raise ValidationError(_("Rit en lijn komen niet overeen"))

        return cleaned_data

    def form_valid(self, form):
        ret = super(Kv17ChangeForm, self).form_valid(form)
        self.create_journeychange(form)
        return ret

    def create_journeychange(self, form):
        change = Kv17JourneyChange(change=form.instance)
        change.reasontype = self.cleaned_data['reasontype']
        change.subreasontype = self.cleaned_data['subreasontype']
        change.reasoncontent = self.cleaned_data['reasoncontent']
        change.advicetype = self.cleaned_data['advicetype']
        change.subadvicetype = self.cleaned_data['subadvicetype']
        change.advicecontent = self.cleaned_data['advicecontent']
        change.save()

    class Meta:
        model = Kv17Change
        exclude = [ 'dataownercode', 'is_recovered', 'reinforcement']
        widgets = {
            'line': forms.HiddenInput(),
            'journey': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(Kv17ChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('line', id='line'),
            Field('journey', id='journey'),
            Accordion(
                AccordionGroup(_('Oorzaak'),
                       'reasontype',
                       'subreasontype',
                       'reasoncontent'
                ),
                AccordionGroup(_('Advies'),
                       'advicetype',
                       'subadvicetype',
                       'advicecontent'
                )
            )
        )


class PlanScenarioForm(forms.Form):
    messagestarttime = forms.DateTimeField(label=_("Begin"), initial=now)
    messageendtime = forms.DateTimeField(label=_("Einde"), initial=get_end_service)

    def clean(self):
        data = self.cleaned_data
        if self.data['messageendtime'] <= self.data['messagestarttime']:
            raise ValidationError(_("Einde moet na begin zijn"))
        return data

    def __init__(self, *args, **kwargs):
        super(PlanScenarioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = 'scenario_plan'
        self.helper.layout = Layout(
            # Put in two columns
            Div(Div(Field('messagestarttime'), css_class="col-sm-6 col-lg-6"),
                Div(Field('messageendtime'), css_class="col-sm-6 col-lg-6"),
                css_class="row"),
            Submit('submit', _("Plan alle berichten in"))
        )

class CancelLinesForm(forms.Form):
    verify_ok = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    def clean_verify_ok(self):
        if self.cleaned_data.get('verify_ok') is not True:
            raise ValidationError(_("Je moet goedkeuring geven om alle lijnen op te heffen"))

    def __init__(self, *args, **kwargs):
        super(CancelLinesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = 'journey_redbutton'
        self.helper.layout = Layout(
            Hidden('verify_ok', 'true'),
            Submit('submit', _("Hef alle ritten op"), css_class="text-center btn-danger btn-tall col-sm-3 pull-right")
        )