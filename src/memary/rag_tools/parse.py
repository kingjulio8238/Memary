def parse_fn(self, output: str) -> list[str]:
    matches = output.strip().split("^")

    # capitalize to normalize with ingestion
    return [x.strip().capitalize() for x in matches if x.strip()]