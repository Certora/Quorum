import re


class ReportGenerator:
    '''
    Description
    -----------
    This class generates a report from a template and tags. It is responsible to replace all tags
    with their correct values and also handle special "loop" command tags that can dynamically 
    expand the report with multiple entries.
    '''
    LOOP_COMMAND = 'loop'

    def __init__(self, template: str, tag_mappings: dict[str, str | list[str]]) -> None:
        '''
        Summary
        -------
        Creates a report. Access the report using `instance.report`.

        Parameters
        ----------
        template : str
            The template string to generate the report from.
        tag_mappings : dict[str, str | list[str]]
            A mapping from tags to their values. The values can be a single string or a list of string (for loops).
        '''
        self.report = self.__generate_report(template, tag_mappings)

    @staticmethod
    def __generate_report(template: str, tag_mappings: dict[str, str | list[str]]) -> str:
        '''
        Summary
        -------
        Main function to generate a report.

        Parameters
        ----------
        template : str
            The template string to generate the report from.
        tag_mappings : dict[str, str | list[str]]
            A mapping from tags to their values. The values can be a single string or a list of string (for loops).
        
        Returns
        -------
        str
            The report.
        '''
        res = ReportGenerator.__replace_loops(template, tag_mappings)
        res = ReportGenerator.__fill_tags(res, tag_mappings)
        return res
    
    @staticmethod
    def __fill_tags(template: str, tag_mappings: dict[str, str | list[str]]) -> str:
        '''
        Summary
        -------
        Fills `<tag>` patterns in the template with their values.
        If the specified value in the mapping is a list. It will ignore it.

        Parameters
        ----------
        template : str
            The template string to generate the report from.
        tag_mappings : dict[str, str | list[str]]
            A mapping from tags to their values. The values can be a single string or a list of string (for loops).
        
        Returns
        -------
        str
            The report after filling the tags.
        '''
        res = template
        for tag, value in tag_mappings.items():
            if isinstance(value, str):
                res = res.replace(f'<{tag}>', value)
        return res

    @staticmethod
    def __replace_loops(template: str, tag_mappings: dict[str, str | list[str]]) -> str:
        '''
        Summary
        -------
        Replaces each all loop commands with the list of relevant values.

        Parameters
        ----------
        template : str
            The template string to generate the report from.
        tag_mappings : dict[str, str | list[str]]
            A mapping from tags to their values. The values can be a single string or a list of string (for loops).
        
        Returns
        -------
        str
            The report with all values replaced.
        '''
        pattern = rf'<{ReportGenerator.LOOP_COMMAND}:([^>]+)>'
        matches = re.findall(pattern, template)
        res = template
        for m in matches:  # The match string contains only the tags we're looping over.
            loop_tag_mapping = {tag: tag_mappings[tag] for tag in m.split(',')}
            res = ReportGenerator.__unroll_loop(res, m, loop_tag_mapping)
        return res
    
    @staticmethod
    def __unroll_loop(template: str, looping_tags: str, loop_tag_mappings: dict[str, list[str]]) -> str:
        '''
        Summary
        -------
        Unrolls a loop in the report.

        Parameters
        ----------
        template : str
            The template string to generate the report from.
        looping_tags : str
            The string representing the tags we're looping over. For example "tag1,tag2".
        loop_tag_mappings : dict[str, list[str]]
            The mapping from each tag we're looping over to it's list of values. The values will be added
            in order so first value of tag1 will be matched with first value of tag2 and so on.
        
        Returns
        -------
        str
            The report with all values replaced.
        '''
        start_tag = f'<{ReportGenerator.LOOP_COMMAND}:{looping_tags}>'
        end_tag = f'</{ReportGenerator.LOOP_COMMAND}>'

        start_index = template.index(start_tag) + len(start_tag)
        end_index = template.index(end_tag)

        loop_template = template[start_index:end_index].strip()

        loop_result = ReportGenerator.__build_loop_content(loop_template, loop_tag_mappings)

        return template[:template.index(start_tag)] + loop_result + template[end_index + len(end_tag):]
    
    @staticmethod
    def extract_loop_values_lengths(values: list[list[str]]) -> int:
        '''
        Summary
        -------
        Returns the length of the values lists for a loop while also asserting all lists have the same length.

        Parameters
        ----------
        values : list[list[str]]
            The lists of values to be replaced in the loop.
        
        Returns
        -------
        int
            The length of the loop.
        
        Raises
        ------
        ValueError
            If all list does not have the same length.
        '''
        expected_length = len(values[0])
        for v in values:
            if len(v) != expected_length:
                raise ValueError('lengths not equal')
        return expected_length

    @staticmethod
    def __build_loop_content(loop_template: str, loop_tag_mappings: dict[str, list[str]]) -> str:
        '''
        Summary
        -------
        Multiplies the loop template based on the number of values we have to in the mappings and
        replaces the values in each iteration of the loop.

        Parameters
        ----------
        loop_template : str
            The template the loop has.
        loop_tag_mappings : dict[str, list[str]]
            The mapping from each tag we're looping over to it's list of values. The values will be added
            in order so first value of tag1 will be matched with first value of tag2 and so on.
        
        Returns
        -------
        str
            The report with all values replaced.
        '''
        loop_count = ReportGenerator.extract_loop_values_lengths(list(loop_tag_mappings.values()))
        res = ''
        for i in range(loop_count):
            res += ReportGenerator.__fill_tags(loop_template, 
                                               {tag: values[i] for tag, values in loop_tag_mappings.items()}) + '\n'
        return res.strip()