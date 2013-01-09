from src_index import app
class XmlGenerator():
    '''
    '''
    
    def __init__(self):
        self.out='<program>'
        self.data_diagram={} # diagram in json format
        self.data_objs=[]    # diagram in list
        self.dict_elems={}   # elements(contact, coil, inst) in dict
        self.list_all_elem=['open_contact', 'close_contact', 'coil', 'timer', \
                            'counter', 'reg']
        self.list_outputs = ['coil', 'timer', 'counter', 'register']
        self.node_list={}
        self.paths = {}
        # self.dict_elems:
        # {'y0': {'item_name': 'y0', 'item_type': 'coil.jpeg', 'item_value': 'None'}, ... }
    
    def elements_init(self):
        '''
        <elements>
        </elements>
        '''
        self._add_to_document('<elements>')
        for obj in self.dict_elems:
            tmp = self.dict_elems[obj]
            if(tmp['item_type'].split('.')[0]=='open_contact'):
                xml_str = '<contact id="%s" normal="true" />'%tmp['item_name']
                if(self.out.find(xml_str)==-1):
                    self._add_to_document(xml_str)
            elif(tmp['item_type'].split('.')[0]=='close_contact'):
                xml_str = '<contact id="%s" normal="false" />'%tmp['item_name']
                if(self.out.find(xml_str)==-1):
                    self._add_to_document(xml_str)
            elif(tmp['item_type'].split('.')[0]=='coil'):
                xml_str = '<coil id="%s" type="%s" />'%(tmp['item_name'], tmp['item_set_type'])
                if(self.out.find(xml_str)==-1):
                    self._add_to_document(xml_str)
            elif(tmp['item_type'].split('.')[0]=='timer'):
                xml_str = '<timer id="%s" delay="%s" unit="ms" />'%(tmp['item_name'], tmp['item_delay'])
                if(self.out.find(xml_str)==-1):
                    self._add_to_document(xml_str)
            elif(tmp['item_type'].split('.')[0]=='counter'):
                xml_str = '<counter id="%s" countTo="%s" target="%s" />'%(tmp['item_name'], tmp['item_countTo'], tmp['item_target'])
                if(self.out.find(xml_str)==-1):
                    self._add_to_document(xml_str)
            elif(tmp['item_type'].split('.')[0]=='register'):
                xml_str = '<reg id="%s" />'%(tmp['item_name'])
                if(self.out.find(xml_str)==-1):
                    self._add_to_document(xml_str)
                
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
    
    
    def adjust_data(self, data_objs):
        for i in range(0, len(data_objs)):
            a = data_objs[i].item_type.split('.')[0]
            if '/' in a:
                a = a.split('/')[1]
            data_objs[i].item_type = a
        return data_objs
    
    def start(self, json_data):
        self.data_diagram = json_data 
        data = self.data_diagram    
        self.data_objs = [0]*(len(data)*len(data['row_0'])) 
        
        for row in data:
            for cell in data[row]:
                if(data[row][cell]["item_name"]!="None"):
                    self.dict_elems[data[row][cell]["id"]] = data[row][cell]
                self.data_objs[data[row][cell]["id"]] = Cell(data[row][cell])
                
        self.data_objs = self.adjust_data(self.data_objs)
        self.elements_init()
        tmp=0
        for i in self.data_objs:
            if(i.item_type in self.list_outputs and i.id_cell == 10):
                tmp+=1
            elif(i.item_type in self.list_outputs and i.id_cell != 10):
                raise CellError(i.id_cell, i.id_row)
            elif(i.item_type not in self.list_outputs and i.item_type!='None' and i.id_cell == 10):
                raise NoOutputsError()
        if tmp==0:
            raise NoOutputsError()
        
        self._add_to_document('<diagram>')
        
        wSTART = 'Start'
        self.wEND = None   
        
        # find all the outputs, Y0, ...
        for i in self.data_objs:
            if i.item_type in self.list_outputs:
                self.node_list[i.id]=[]
                self.wEND = i # wEnd equals Y0 element cell_object
                
                self.wEND.node = Node()
                self.wEND.node.id = 'End'
                self._add_to_document('<output id="%s">'%self.wEND.item_name)
                
        #//         Find path to begining for all outputs
                curr_node = self.wEND.node
                curr_cell = self.wEND
                
                curr_cell = self.wEND
                curr_path = Path(curr_cell.node)
                
                
                output_id = i.id
                prev_cell=curr_cell
                self.visit_mark(curr_cell, prev_cell, curr_node, output_id)
                for i in self.data_objs:
                    i.visited = False
                
                self.paths[output_id] = []
                self.paths[output_id].append(curr_path)
                self.complete_path(curr_cell, prev_cell, curr_node, output_id, curr_path)
                self.group(output_id)
                
                
                tmp = ''
                for i in self.paths[output_id]:
                    tmp += i.elems
                
                if(tmp[0:5] == '<and>' and tmp[-6:] == '</and>'):
                    self._add_to_document(tmp)
                else:
                    self._add_to_document('<and>')
                    self._add_to_document(tmp)
                    self._add_to_document('</and>')
                
                self._add_to_document('</output>')
                Node.node_counter = 0
                Path.path_counter = 0
        
        self._add_to_document('</diagram>')  
        self._add_to_document('</program>')
        return self.out
    
    def group(self, output_id):
        paths = self.paths[output_id]
        def same():
            ret = False
            # I. Find the same
            for i in paths:
                for j in paths:
                    # II. Find pairs where 1st the same
                    if(i!=j and i.start_node == j.start_node):
                        i.group = True
                        j.group = True
                        if(i.stop_node.id == j.stop_node.id):
                            if(i.elems.find('<or>') == 0):
                                i.elems = ''.join([i.elems[0:-6], '\n', j.elems, '\n</or>'])
                            elif(j.elems.find('<or>') == 0):
                                i.elems = ''.join([j.elems[0:-6], '\n', i.elems, '\n</or>'])
                            else:
                                i.elems = ''.join(['<or>\n', i.elems, '\n', j.elems, '\n</or>'])
                            paths.remove(j)
                            ret = True
            return ret
        def related():
            same()    
            ret = False
            for i in paths:
                if (i.group == True):
                    for j in paths:
                        if(i!=j and i.stop_node == j.start_node and j.elems == '' and i.elems == ''):
                            i.stop_node = j.stop_node
                            paths.remove(j)
                            return True                        
                        elif(i!=j and i.stop_node == j.start_node and j.elems != '' and i.elems == ''):
                            i.elems = j.elems
                            i.stop_node = j.stop_node
                            paths.remove(j)
                            return True   
                        elif(i!=j and i.stop_node == j.start_node and j.elems == '' and i.elems != ''):
                            if(j.stop_node.blank == True):
                                i.stop_node = j.stop_node
                            paths.remove(j)
                            return True   
                        elif(i!=j and i.stop_node == j.start_node and j.elems != '' and i.elems != ''):
                            i.elems = ''.join(['<and>\n', i.elems, '\n', j.elems, '\n</and>'])
                            i.stop_node = j.stop_node
                            paths.remove(j)
                            return True            
            return False
            
        while( related() ):
            pass
        
            
    
    def complete_path(self, curr_cell, prev_cell, curr_node, output_id=10, curr_path=None):
        dirs = self.what_direction(curr_cell, prev_cell)
        if(curr_cell.item_type in self.list_all_elem):
            curr_path.add_to_path(curr_cell)
                
        if ['blank'] == dirs:
            curr_cell.visited = True
            curr_cell.node.blank = True
        else:
            if curr_cell.visited == False:
                curr_cell.visited = True
                
                if(isinstance(curr_cell.node, Node)):
                    if(curr_cell.node.blank == True and curr_cell.item_type in ['hor-down', 'ver-right', 'top-right'] and curr_cell.node.id=='Start'):
                        self.paths[output_id][curr_path.id].stop_node = curr_cell.node
                    elif (curr_cell.node.blank == True and curr_cell.item_type =='hor' and curr_cell.node.id=='Start'):
                        self.paths[output_id][curr_path.id].stop_node = curr_cell.node
                    elif (curr_cell.node.blank == True and curr_cell.node.id=='Start'):
                        self.paths[output_id][curr_path.id].stop_node = curr_cell.node
                    elif(curr_cell.node.blank == True and curr_cell.item_type in ['hor-down', 'ver-right', 'top-right']):
                        self.paths[output_id][curr_path.id].stop_node = curr_cell.node
                        if (curr_cell.item_type == 'hor-down'):
                            curr_path = Path(curr_cell.node)
                            self.paths[output_id].append(curr_path)
                        self.complete_path(dirs[0], curr_cell, curr_cell.node, output_id, curr_path)
                    elif(curr_cell.node.blank == False): 
                                                
                        if (curr_cell.item_type == 'hor-down'):
                            self.paths[output_id][curr_path.id].stop_node = curr_cell.node
                            curr_path = Path(curr_cell.node)
                            self.paths[output_id].append(curr_path)
                            self.complete_path(dirs[0], curr_cell, curr_cell.node, output_id, curr_path)# curr_path = new Path
                            curr_path = None
                            if(curr_cell.node.id != 'Start'): self.complete_path(dirs[1], curr_cell, curr_cell.node, output_id, curr_path)# curr_path = None
                        elif (curr_cell.item_type == 'ver-left'):
                            
                            curr_path = Path(curr_cell.node)
                            self.paths[output_id].append(curr_path)
                            self.complete_path(dirs[0], curr_cell, curr_cell.node, output_id, curr_path)# curr_path = new Path
                            curr_path = None
                            self.complete_path(dirs[1], curr_cell, curr_cell.node, output_id, curr_path)# curr_path = None
                        elif (curr_cell.item_type == 'left-top'):
                            
                            curr_path = Path(curr_cell.node)
                            self.paths[output_id].append(curr_path)
                            self.complete_path(dirs[0], curr_cell, curr_cell.node, output_id, curr_path)# curr_path = new Path
                        elif(curr_cell.item_type == 'ver'):
                            self.complete_path(dirs[0], curr_cell, curr_cell.node, output_id, curr_path)
                else:
                    for i in dirs:
                        self.complete_path(i, curr_cell, curr_cell.node, output_id, curr_path)
    
    
    def visit_mark(self, curr_cell, prev_cell, curr_node, output_id=10):
        # add node marking, if branch is visited and blank: sth
        dirs = self.what_direction(curr_cell, prev_cell)
        
                
        if(curr_cell.visited == False):
            if(dirs == ['Start']):
                curr_cell.node = Node()
                curr_cell.node.id = 'Start'
                curr_cell.node.blank = True
            elif(curr_cell.item_type == 'hor-down'):
                if(curr_node == None or prev_cell.item_type == 'hor-down'):
                    curr_cell.node = Node(curr_cell)
                    self.node_list[output_id].append(curr_cell)
                else:
                    curr_cell.node = curr_node
            elif(curr_cell.item_type == 'hor-top'):
                if(curr_node == None):
                    curr_cell.node = Node(curr_cell)
                    self.node_list[output_id].append(curr_cell)
                else:
                    curr_cell.node = curr_node
                    curr_cell.node.row_num += 1
            elif(curr_cell.item_type in ['ver-right', 'ver-left', 'top-right', 'left-top', \
                                 'down-right', 'left-down', 'ver']):
                curr_cell.node = curr_node
                if curr_node != None:
                    curr_cell.node.row_num += 1
            else:
                curr_cell.node = None 
        elif(curr_cell.visited == True and curr_cell.item_type == 'top-right' and curr_node != None):
            prev_cell.node = curr_cell.node
                            
            
        if ['Start'] == dirs:
            curr_cell.node = Node()
            curr_cell.node.id = 'Start'
            curr_cell.visited = True
            curr_cell.node.blank = True
        elif ['Error'] == dirs or dirs == None or None in dirs:
            raise CellError(curr_cell.id_cell, curr_cell.id_row)
        elif ['blank'] == dirs:
            curr_cell.visited = True
            curr_cell.node.blank = True
        else:
            if 'Start' in dirs:
                dirs.remove('Start')
                curr_cell.node = Node()
                curr_cell.node.id = 'Start'
                curr_cell.node.blank = True
            if curr_cell.visited == False:
                curr_cell.visited = True
                for i in dirs:
                    self.visit_mark(i, curr_cell, curr_cell.node, output_id)
        
        
    def what_direction(self, cell, prev_cell):
        ''' return next list of next cells
        '''
        if((cell.item_type == 'hor-down' and prev_cell == self.get_cell_obj(cell.id_cell+1, cell.id_row)) or \
             (cell.item_type == 'ver-left' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row-1))):
            # left and down
            l = self.get_cell_obj(cell.id_cell-1, cell.id_row)
            d = self.get_cell_obj(cell.id_cell, cell.id_row+1)
            if(cell.id_cell == 0):
                l = 'Start'
            return [l, d]
        elif((cell.item_type == 'ver-left' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row+1)) or \
             (cell.item_type == 'hor-top' and prev_cell == self.get_cell_obj(cell.id_cell+1, cell.id_row))): 
            # left and top
            l = self.get_cell_obj(cell.id_cell-1, cell.id_row)
            t = self.get_cell_obj(cell.id_cell, cell.id_row-1)
            if(cell.id_cell == 0):
                l = 'Start'
            return [l, t]
        elif((cell.item_type == 'hor-top' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row-1)) or \
              (cell.item_type == 'hor') or (cell.item_type == 'left-down') or (cell.item_type == 'left-top') or \
              (cell.item_type == 'hor-down' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row+1)) or \
              (cell.item_type in ['open_contact', 'close_contact'] or cell.item_type in self.list_outputs)): 
            # left 
            l = self.get_cell_obj(cell.id_cell-1, cell.id_row)
            if(cell.id_cell == 0):
                l = 'Start'
            return [l]
        elif((cell.item_type == 'down-right' and prev_cell == self.get_cell_obj(cell.id_cell+1, cell.id_row)) or \
             (cell.item_type == 'ver-right' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row-1)) or \
             (cell.item_type == 'ver' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row-1))): 
            # down     
            d = self.get_cell_obj(cell.id_cell, cell.id_row+1)
            return [d]
        elif(cell.item_type == 'ver-right' and prev_cell == self.get_cell_obj(cell.id_cell+1, cell.id_row) ):
            # top and down
            t = self.get_cell_obj(cell.id_cell, cell.id_row-1)
            d = self.get_cell_obj(cell.id_cell, cell.id_row+1)
            return [t, d]
        elif(cell.item_type == 'ver-right' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row+1) ) or \
             (cell.item_type == 'top-right' and prev_cell == self.get_cell_obj(cell.id_cell+1, cell.id_row)) or \
             (cell.item_type == 'ver' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row+1)):
            # top
            t = self.get_cell_obj(cell.id_cell, cell.id_row-1)
            return [t]        
        elif((cell.item_type == 'down-right' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row+1)) or \
             (cell.item_type == 'top-right' and prev_cell == self.get_cell_obj(cell.id_cell, cell.id_row-1))):
            # blank branch
            return ['blank']
        else:
            raise CellError(cell.id_cell, cell.id_row)
       
    def get_cell_obj(self, id_cell, id_row):
        ''' @param id_cell: 0 - 10 '''
        for i in self.data_objs:
            if (i.id_cell == id_cell and i.id_row == id_row):
                return i

class Cell():
    '''
    attr = {
    this.id_row;
    this.id_cell;
    this.item_id = id;
    this.item_type = 'None';
    this.item_name = 'None';
    }
    '''
    def __init__(self, attr):
        self.id = attr['id']
        self.item_type = attr['item_type']
        self.item_name = attr['item_name']
        self.item_set_type = attr['item_set_type']  
        self.item_delay = attr['item_delay']  
        self.item_target = attr['item_target']  
        self.item_countTo = attr['item_countTo']  
        self.id_row = attr['id_row']  
        self.id_cell = attr['id_cell']  
        self.node = None   
        self.visited = False  

class Node():
    node_counter = 0
    def __init__(self, curr_cell=None):
        self.id = Node.node_counter
        Node.node_counter+=1
        self.blank = False
        self.mark = False
        self.id_cell = None if curr_cell==None else curr_cell.id_cell
        self.id_row = None if curr_cell==None else curr_cell.id_row
        self.row_num = 1

class Path():
    path_counter = 0
    def __init__(self, start_node):
        self.id = Path.path_counter    
        Path.path_counter +=1
        self.start_node = start_node
        self.stop_node = None
        self.elems = ''
        self.elem_num = 0
        self.group = False
        
    def add_to_path(self, cell):
        if(cell.item_type not in ['coil', 'set', 'reset', 'timer', 'counter', 'register']):
            self.elem_num += 1
            tmp = '<elem id="%s" />'%cell.item_name
            if(self.elem_num == 1):
                self.elems = tmp
            elif(self.elem_num == 2):
                self.elems = '<and>\n'+self.elems+'\n'+tmp+'\n</and>'
            else:
                self.elems = ''.join([self.elems[0:-7],'\n',tmp,'\n</and>'])
        
        
    
class NoOutputsError(Exception):
    pass
class CellError(Exception):
    def __init__(self, id_cell, id_row):
        self.id_cell = id_cell
        self.id_row = id_row
        
        
        
        