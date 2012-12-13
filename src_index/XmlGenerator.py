from src_index import app
class XmlGenerator():
    '''
    data = eval(data.read())
    '''
    
    def __init__(self):
        self.out='<program>'
        self.dict_elems={}
    
    def elements_init(self):
        '''
        <elements>
        </elements>
        '''
        self._add_to_document('<elements>')
        for obj in self.dict_elems:
            tmp = self.dict_elems[obj]
            print(tmp)
            if(tmp['item_type'].split('.')[0]=='open_contact'):
                xml_str = '<contact id="%s" normal="true" />'%tmp['item_name']
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='close_contact'):
                xml_str = '<contact id="%s" normal="false" />'%tmp['item_name']
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='coil'):
                xml_str = '<coil id="%s" />'%tmp['item_name']
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='set'):
                # should be <coil> or <reg ????
                xml_str = '<reg id="%s" type="set" />'%tmp['item_name']
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='reset'):
                xml_str = '<reg id="%s" type="reset" />'%tmp['item_name']
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='timer'):
                xml_str = '<timer id="%s" delay="%s" target="true" unit="ms" />'%(tmp['item_name'], tmp['item_value'])
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='counter'):
                xml_str = '<counter id="%s" countTo="%s" target="false" />'%(tmp['item_name'], tmp['item_value'])
                self._add_to_document(xml_str)
            if(tmp['item_type'].split('.')[0]=='register'):
                # ??????????
                pass
            if(tmp['item_type'].split('.')[0]=='pls'):
                pass
            if(tmp['item_type'].split('.')[0]=='plf'):
                pass
                
        self._add_to_document('</elements>')
    
    def _add_to_document(self, text):
        self.out = self.out+"\n"+text
        
    def add_element(self, name, attrs):
        '''
        <elem id="x1" />
        '''
        self._add_to_document('<' + name)
        for (name, value) in attrs.items():
            self._add_to_document(' %s=%s' % (name, value))
        self._add_to_document(' />')
    
    def start_element(self, out, name, attrs):
        self._add_to_document('<' + name)
        for (name, value) in attrs.items():
            self._add_to_document(' %s=%s' % (name, value))
        self._add_to_document('>')
        
    def end_element(self, name):
        self._add_to_document('</%s>' % name)
        
    def start(self, json_data):
        data = json_data
        for row in data:
            for cell in data[row]:
                if(data[row][cell]["item_name"]!="None"):
                    self.dict_elems[data[row][cell]["item_name"]] = data[row][cell] 
        self.elements_init()
        
        self._add_to_document('</program>')
        return self.out
            
        