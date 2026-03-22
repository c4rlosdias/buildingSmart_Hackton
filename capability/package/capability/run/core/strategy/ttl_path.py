from ontobdc.run.core.port.contex import CliContextPort, CliContextStrategyPort


class OntoPathStrategy(CliContextStrategyPort):
    def execute(self, context: CliContextPort) -> CliContextPort:
        unprocessed_args = context.unprocessed_args

        onto_paths: list[str] = []
        while "--onto-path" in unprocessed_args:
            idx = unprocessed_args.index("--onto-path")
            if idx + 1 >= len(unprocessed_args):
                raise ValueError("Missing value for --onto-path.")
            val = unprocessed_args[idx + 1]
            onto_paths.append(val)
            context.clear_parameters(["--onto-path", val])

        if onto_paths:
            context.add_parameter(
                "onto_path",
                {
                    "value": onto_paths,
                    "uri": "org.local.domain.context.strategy.parameter.onto_path",
                    "param_uri": "org.local.domain.ontology.input.path",
                },
            )

        if "--ids-output-path" in unprocessed_args:
            idx = unprocessed_args.index("--ids-output-path")
            if idx + 1 < len(unprocessed_args):
                val = unprocessed_args[idx + 1]
                context.add_parameter(
                    "ids_output_path",
                    {
                        "value": val,
                        "uri": "org.local.domain.context.strategy.parameter.ids_output_path",
                        "param_uri": "org.local.domain.ids.output.path",
                    },
                )
                context.clear_parameters(["--ids-output-path", val])
            else:
                raise ValueError("Missing value for --ids-output-path.")

        return context
