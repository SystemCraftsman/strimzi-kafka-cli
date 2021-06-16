import click


class NotRequiredIf(click.Argument):
    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.arguments = kwargs.pop('arguments')
        assert self.arguments, "'arguments' parameter required"
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_arguments_exist = False

        for arguments in self.arguments:
            control_arguments_exist = arguments in opts
            if control_arguments_exist is True:
                break

        if control_arguments_exist:
            self.required = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)


class RequiredIf(click.Argument):

    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.arguments = kwargs.pop('arguments')
        assert self.arguments, "'arguments' parameter required"
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_arguments_exist = False

        for arguments in self.arguments:
            control_arguments_exist = arguments in opts
            if control_arguments_exist is True:
                break

        if control_arguments_exist:
            self.required = True
        else:
            self.required = None

        return super(RequiredIf, self).handle_parse_result(
            ctx, opts, args)
