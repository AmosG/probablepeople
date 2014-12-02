import name_parser
from lxml import etree
import os

# given a list of labeled sequences to an xml list, 
# appends corresponding xml to existing xml
# format for list_to_append:    [   [ (token, label), (token, label), ...],
#                                   [ (token, label), (token, label), ...],
#                                   [ (token, label), (token, label), ...],
#                                   ...           ]
# calls sequence2XML
# called by appendListToXMLfile
def appendListToXML(list_to_append, collection_XML) :
    for labeled_sequence in list_to_append:
        sequence_xml = sequence2XML(labeled_sequence)
        collection_XML.append(sequence_xml)
    return collection_XML


# given a labeled sequence in the form of [(token, label), (token, label), ...]
# generates xml for that sequence
# called by appendListToXML
def sequence2XML(labeled_sequence) :
    parent_tag = name_parser.config.PARENT_LABEL
    sequence_xml = etree.Element(parent_tag)

    for token, label in labeled_sequence:
        component_xml = etree.Element(label)
        component_xml.text = token
        component_xml.tail = ' '
        sequence_xml.append(component_xml)
    sequence_xml[-1].tail = ''
    return sequence_xml


# formatting for an xml collection
def stripFormatting(collection) :
    collection.text = None 
    for element in collection :
        element.text = None
        element.tail = None
        
    return collection


# appends a labeled list to an xml file
# calls appendListToXML, stripFormatting
# format for labeled_list:      [   [ (token, label), (token, label), ...],
#                                   [ (token, label), (token, label), ...],
#                                   [ (token, label), (token, label), ...],
#                                   ...           ]
def appendListToXMLfile(labeled_list, filepath):

    if os.path.isfile(filepath):
        with open( filepath, 'r+' ) as f:
            tree = etree.parse(filepath)
            collection_XML = tree.getroot()
            collection_XML = stripFormatting(collection_XML)

    else:
        collection_tag = name_parser.config.GROUP_LABEL
        collection_XML = etree.Element(collection_tag)

    collection_XML = appendListToXML(labeled_list, collection_XML)

    with open(filepath, 'w') as f :
        f.write(etree.tostring(collection_XML, pretty_print = True)) 


# given a list of filenames (containing xml),
# outputs an xml file with the contents of all the xml files
def smushXML( xml_infile_list, xml_outfile ):

    collection_tag = name_parser.config.GROUP_LABEL
    full_xml = etree.Element(collection_tag)
    component_string_list = []

    for xml_infile in xml_infile_list:
        if os.path.isfile(xml_infile):
            with open( xml_infile, 'r+' ) as f:
                tree = etree.parse(f)
                file_xml = tree.getroot()
                file_xml = stripFormatting(file_xml)
                for component_etree in file_xml:
                    # etree components to string representations
                    component_string_list.append(etree.tostring(component_etree))
        else:
            print "WARNING: %s does not exist" % xml_infile
    # get rid of duplicates in string representations
    component_string_list = list(set(component_string_list))
    # unique string representations back to etree
    for component_string in component_string_list:
        xml = etree.fromstring(component_string)
        full_xml.append(xml)

    with open( xml_outfile, 'w' ) as f:
        f.write( etree.tostring(full_xml, pretty_print = True) )


# writes strings to a file
def list2file(string_list, filepath):
    file = open( filepath, 'w' )
    for string in string_list:
        file.write('"%s"\n' % string)


def parseTrainingData(filepath):
    tree = etree.parse(filepath)
    collection_XML = tree.getroot()

    for sequence_xml in collection_XML:
        components = []
        string_concat = etree.tostring(sequence_xml, method='text')
        string_concat = string_concat.replace('&#38;', '&')
        for component in list(sequence_xml):
            components.append([component.text, component.tag])
            if component.tail and component.tail.strip():
                components.append([component.tail.strip(), NULL_TAG])

        yield string_concat, components

if __name__ == '__main__':

    smushXML( ['training/training_data/manually_labeled.xml', 'training/training_data/labeled.xml'], 'training/training_data/labeled.xml' )