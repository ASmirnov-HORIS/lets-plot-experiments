from examples import EXAMPLES

examples_list = "\n".join([
    "{0}.\nRequest: {1}\nResponse:\n{2}\n".format(i + 1, example.request, example.response)
    for i, example in enumerate(EXAMPLES)
])

class Text2Spec:
    SYSTEM_PROMPT = (r"""
There is a plotting library Lets-Plot, based on grammar of graphics with ggplot2-like API.
Lets-Plot can build plots based on JSON specification.
Your task is to generate correct specification for this library based on user's request.

Here is the basic information about the specification:

{
  "data": data, dict,
  "mapping": mapping between data columns and aesthetics, dict,
  "data_meta": {
    "series_annotations": data column types, list
  },
  "kind": "plot",
  "scales": scales specification, list,
  "layers": [
    {
      "geom": geometry type,
      "mapping": mappings for this layer, dict,
      "data_meta": {
        "series_annotations": layer data column types
      }
    }
  ]
}
""" + """
Examples:

{0}
""".format(examples_list)
).strip()

    def __init__(self, api_key, *,
                 model="gpt-4o-mini",
                 temperature=1.0):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def query(self, message):
        import json
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        return json.loads(self._get_response(messages))

    def _get_response(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        return response.choices[0].message.content