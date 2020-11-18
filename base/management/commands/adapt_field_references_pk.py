import json

from django.core.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('starting_from', nargs='+', type=int, help='Pk from which adaptation will be done')

    def handle(self, *args, **options):
        path = "rules_management/fixtures/field_reference.json"

        if not options['starting_from']:
            self.stdout.write("You must specify the pk from which adaptation will be done")
        else:
            confirm = input("All pk's following {} in field_reference.json will be overwritten. Proceed? (y/n)".format(
                options['starting_from'][0]
            ))
            while 1:
                if confirm not in ('y', 'n', 'yes', 'no'):
                    confirm = input('Please enter either "yes" or "no": ')
                    continue
                if confirm in ('y', 'yes'):
                    break
                else:
                    self.stdout.write("Cancelled by user. File will remain untouched")
                    return
            self.adapt_field_references_pk(path, options['starting_from'][0])

    def adapt_field_references_pk(self, file_path: str, starting_from: int):
        with open(file_path, 'r') as f:
            data = json.load(f)

        last_pk = starting_from
        starting_from_found = False
        for obj in data:
            if obj['pk'] <= last_pk and not starting_from_found:
                starting_from_found = obj['pk'] == starting_from
                continue
            if obj['pk'] != last_pk + 1:
                obj['pk'] = last_pk + 1
            last_pk = obj['pk']

        f.close()

        if starting_from_found:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                f.close()
            self.stdout.write('Successfully replaced references primary keys starting from : ' + str(starting_from))
        else:
            self.stdout.write('Did not find pk {}'.format(starting_from))
