from django.shortcuts import render
# Create your views here.
from django.views.generic import TemplateView

from system.minimizer import Minimizer


class HomeView(TemplateView):
    template_name = 'system/index.html'
    minimizer = None

    def dispatch(self, request, *args, **kwargs):
        response = 'hello'
        # implicants = [self.implicant_to_str([0, 0, 0, 1])]
        context = {}

        if request.method == 'POST':
            args_count = self.request.POST.get('args_count')
            args = list(map(lambda x: int(x), self.request.POST.get('args').split(' ')))
            minimizer = Minimizer(args_count, args)
            implicants = list(map(lambda x: self.implicant_to_str(x), minimizer.find_primary_implicants()))
            terms = list(map(lambda x: self.implicant_to_str(x), minimizer.terms))
            table = minimizer.build_coverage_table()
            context = {'response': response, 'primary_implicants': implicants, 'terms': terms, 'table': table}
        return render(request, self.template_name, context)

    def implicant_to_str(self, implicant):
        string = ''

        for i in range(len(implicant)):
            if implicant[i] == 1:
                string += 'X' + str(i + 1) + ' '
            elif implicant[i] == 0:
                string += "!X" + str(i + 1) + ' '

        return string
