from django.shortcuts import render
# Create your views here.
from django.views.generic import TemplateView

from system.minimizer import Minimizer


class HomeView(TemplateView):
    template_name = 'system/index.html'
    minimizer = None

    def dispatch(self, request, *args, **kwargs):
        response = 'hello'
        context = {}

        if request.method == 'POST':
            args_count = self.request.POST.get('args_count')
            args = list(map(lambda x: int(x), self.request.POST.get('args').split(' ')))
            minimizer = Minimizer(args_count, args)
            terms = ' v '.join(list(map(lambda x: self.implicant_to_str(x), minimizer.terms)))

            first_implicants = [x for x in list(map(lambda x: self.implicant_to_str(x), minimizer.find_primary_implicants()))]
            table = minimizer.build_coverage_table()
            primary_implicants = minimizer.find_core_implicants(table)

            boolean_implicants = [x for x in list(map(lambda x: self.implicant_to_str(x), primary_implicants))]
            sheffer_implicants = [x for x in list(map(lambda x: self.implicant_to_sheffer(x), primary_implicants))]
            pearce_implicants = [x for x in list(map(lambda x: self.implicant_to_pearce(x), primary_implicants))]

            context = {
                'first_implicants': first_implicants,
                'response': response,
                'pearce': pearce_implicants,
                'sheffer': sheffer_implicants,
                'boolean': boolean_implicants,
                'terms': terms,
                'table_terms':minimizer.table_terms,
            }

        return render(request, self.template_name, context)

    def implicant_to_str(self, implicant):
        string = '[ '

        for i in range(len(implicant)):
            if implicant[i] == 1:
                string += 'x' + str(i + 1) + ' ^ '
            elif implicant[i] == 0:
                string += "!x" + str(i + 1) + ' ^ '
        string = string[:len(string) - 2]
        string += ' ]'
        return string

    def implicant_to_sheffer(self, implicant):
        string = '[ '

        for i in range(len(implicant)):
            if implicant[i] == 1:
                string += 'x' + str(i + 1) + ' / '
            elif implicant[i] == 0:
                string += "(x{0} / x{0})".format(str(i + 1)) + ' / '
        string = string[:len(string) - 2]
        string += ' ]'
        return string

    def implicant_to_pearce(self, implicant):
        string = '[ '

        for i in range(len(implicant)):
            if implicant[i] == 0:
                string += 'x' + str(i + 1) + ' | '
            elif implicant[i] == 1:
                string += "(x{0} | x{0})".format(str(i + 1)) + ' | '
        string = string[:len(string) - 2]
        string += ' ]'
        return string
