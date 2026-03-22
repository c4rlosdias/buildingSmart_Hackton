from pathlib import Path

from ontobdc.run.core.port.contex import CliContextPort, CliContextStrategyPort


class IcddPathStrategy(CliContextStrategyPort):
    def execute(self, context: CliContextPort) -> CliContextPort:
        unprocessed_args = context.unprocessed_args

        if "--icdd-path" in unprocessed_args:
            idx = unprocessed_args.index("--icdd-path")
            if idx + 1 < len(unprocessed_args):
                raw_val = unprocessed_args[idx + 1]
                val = str(Path(raw_val).expanduser().resolve())

                context.add_parameter(
                    "icdd_path",
                    {
                        "value": val,
                        "uri": "org.local.domain.context.strategy.parameter.icdd_path",
                        "param_uri": "org.local.domain.icdd.input.path",
                    },
                )
                context.clear_parameters(["--icdd-path", raw_val])
            else:
                raise ValueError("Missing value for --icdd-path.")

        return context
