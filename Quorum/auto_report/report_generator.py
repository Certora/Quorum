import re


class ReportGenerator:
    LOOP_COMMAND = 'loop'

    def __init__(self, template: str, tag_mappings: dict[str, str | list[str]]) -> None:
        self.report = self.__generate_report(template, tag_mappings)

    @staticmethod
    def __generate_report(template: str, tag_mappings: dict[str, str | list[str]]) -> str:
        res = ReportGenerator.__replace_loops(template, tag_mappings)
        res = ReportGenerator.__fill_tags(res, tag_mappings)
        return res
    
    @staticmethod
    def __fill_tags(template: str, tag_mappings: dict[str, str | list[str]]) -> str:
        res = template
        for tag, value in tag_mappings.items():
            if isinstance(value, str):
                res = res.replace(f'<{tag}>', value)
        return res

    @staticmethod
    def __replace_loops(template: str, tag_mappings: dict[str, str | list[str]]) -> str:
        pattern = rf'<{ReportGenerator.LOOP_COMMAND}:([^>]+)>'
        matches = re.findall(pattern, template)
        res = template
        for m in matches:
            loop_tag_mapping = {tag: tag_mappings[tag] for tag in m.split(',')}
            res = ReportGenerator.__unroll_loop(res, m, loop_tag_mapping)
        return res
    
    @staticmethod
    def __unroll_loop(template: str, looping_tags: str, loop_tag_mappings: dict[str, list[str]]) -> str:
        start_tag = f'<{ReportGenerator.LOOP_COMMAND}:{looping_tags}>'
        end_tag = f'</{ReportGenerator.LOOP_COMMAND}>'

        start_index = template.index(start_tag) + len(start_tag)
        end_index = template.index(end_tag)

        loop_template = template[start_index:end_index].strip()

        loop_result = ReportGenerator.__build_loop_content(loop_template, loop_tag_mappings)

        return template[:template.index(start_tag)] + loop_result + template[end_index + len(end_tag):]
    
    @staticmethod
    def extract_loop_values_lengths(values: list[list[str]]) -> int:
        expected_length = len(values[0])
        for v in values:
            if len(v) != expected_length:
                raise ValueError('lengths not equal')
        return expected_length

    @staticmethod
    def __build_loop_content(loop_template: str, loop_tag_mappings: dict[str, list[str]]) -> str:
        loop_count = ReportGenerator.extract_loop_values_lengths(list(loop_tag_mappings.values()))
        res = ''
        for i in range(loop_count):
            res += ReportGenerator.__fill_tags(loop_template, 
                                               {tag: values[i] for tag, values in loop_tag_mappings.items()}) + '\n'
        return res.strip()