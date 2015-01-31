class Instruction:
	def __init__(self, t_no, t_op, t_rs, t_rt, t_rd, t_extra):
		self.pc = t_no
		self.op = t_op
		self.rs = t_rs
		self.o_rs = -1
		self.rt = t_rt
		self.o_rt = -1
		self.rd = t_rd
		self.o_rd = -1
		self.extra = t_extra
		self.old_map = None
		self.ready = 0

	def set_rs(self, trs):
		self.o_rs = self.rs
		self.rs = trs

	def set_map(self, omap):
		self.old_map = omap
		
	def set_rt(self, trt):
		self.o_rt = self.rt
		self.rt = trt

	def set_rd(self, trd):
		self.o_rd = self.rd
		self.rd = trd

	def __str__(self):
		return  str(self.pc) + "\t " + str(self.op) + "\t " + str(self.rs) + "\t " + str(self.rt) + "\t " + str(self.rd) + "\t " + str(self.extra) + "\t" + str(self.ready)

class ActiveListEntry:
	def __init__(self, pc, itype, dest, t_extra):
		self.pc = pc
		self.instr_type = itype
		self.log_dest = dest
		self.phy_rs = -1
		self.phy_rt = -1
		self.phy_dest = -1
		self.old_map = None
		self.extra = t_extra
		self.done = 0

	def set_map(self, omap):
		self.old_map = omap

	def set_rs(self, trs):
		self.phy_rs = trs

	def set_rt(self, trt):
		self.phy_rt = trt

	def set_phy(self, phy):
		self.phy_dest = phy

	def __str__(self):
		return str(self.pc) + "\t" + str(self.instr_type) + "\t" + str(self.phy_rs) + "\t" + str(self.phy_rt) + "\t" + str(self.log_dest) + "\t" + str(self.phy_dest) + "\t" + str(self.old_map) + "\t" + str(self.extra) + "\t" + str(self.done) 


class Queue:
	def __init__(self, s, desc):
		self.items = []
		self.qsize = s
		self.desc = desc

	def isEmpty(self):
		return self.items == []	

	def isFull(self):
		return self.size() == self.qsize

	def enqueue(self, item):
		if not self.isFull():
			self.items.insert(0,item)

	def dequeue(self):
		if not self.isEmpty() :
			return self.items.pop()

	def size(self):
		return len(self.items)

	def find_index(self, x):
		for i,e in enumerate(self.items):
			if e != None and e.pc == x.pc :
				return i
		return -1

	def display(self):
		print(self.desc)
		for i in self.items :
			print(i)

	def peek(self):
		return self.items[-1]

	def create_copy(self, result):
		result.items = self.items[:]
		result.qsize = self.qsize	

class Table:

	def __init__(self, s, d):
		self.tsize = s
		self.items = [None for _ in range(s)]
		self.desc = d

	def isFull(self):
		for i in range(self.tsize):
			if self.items[i] == None:
				return False
		return True

	def isEmpty(self):
		for i in range(self.tsize):
			if self.items[i] != None:
				return False
		return True

	def find_place(self):
		for i in range(self.tsize) :
			if self.items[i] == None :
				return i
		return -1

	def find_element(self, elem):
		for i in range(self.tsize):
			if self.items[i] == elem :
				return True
		return False

	def insert(self, index, x):
		if not self.isFull() :
			self.items.insert(index, x)

	def remove(self, index):
		if self.items[index]:
			self.items.__delitem__(index)
			self.items.append(None)

	def find_index(self, x):
		for i,e in enumerate(self.items):
			if e!= None :
				if e.pc == x.pc :
					return i
		return -1

	def find_index_pc(self, x):
		for i,e in enumerate(self.items):
			if e != None :
				if e.pc == x :
					return i
		return -1

	def count(self):
		c = 0
		for i in self.items:
			if i != None :
				c += 1
		return c

	def display(self):
		print(self.desc)
		for x, i in enumerate(self.items) :
			if i != None :
				print(x, i)	

	def create_copy(self, result):
		result.items = self.items[:]
		result.tsize = self.tsize

class MachineState:
	def __init__(self, tPC, i_buffer, fr_list, act_list, m_table, i_queue, f_queue, a_queue, b_stack, bb_table):
		'''
		self.pc = tPC
		self.instr_buffer = i_buffer
		self.free_list = fr_list
		self.active_list = act_list
		self.map_table = m_table
		self.int_queue = i_queue
		self.fp_queue = f_queue
		self.address_queue = a_queue
		self.branch_stack = b_stack
		self.busy_bit_table = bb_table
		'''
		self.pc = tPC
		self.instr_buffer = Queue(8, 'Instruction Buffer')
		self.free_list = Queue(32, 'Free List')
		self.active_list = Table(32, 'Active List')
		self.map_table = Table(32, 'Register Map Table')
		self.int_queue = Table(16, 'Integer Queue')
		self.fp_queue = Table(16, 'Floating Point Queue')
		self.address_queue = Table(16, 'Address Queue')
		self.branch_stack = Table(4, 'Branch Stack')
		self.busy_bit_table = Table(64, 'Busy Bit Table')


		i_buffer.create_copy(self.instr_buffer)
		fr_list.create_copy(self.free_list)
		act_list.create_copy(self.active_list)
		m_table.create_copy(self.map_table)
		i_queue.create_copy(self.int_queue)
		f_queue.create_copy(self.fp_queue)
		a_queue.create_copy(self.address_queue)
		b_stack.create_copy(self.branch_stack)
		bb_table.create_copy(self.busy_bit_table)

	def update_state(self):
		self.pc = PC
		self.instr_buffer = instr_buffer
		self.free_list = free_list
		self.active_list = active_list
		self.map_table = map_table
		self.int_queue = int_queue
		self.fp_queue = fp_queue
		self.address_queue = address_queue
		self.branch_stack = branch_stack
		self.busy_bit_table = busy_bit_table

	def restore_state(self):
		global PC
		global instr_buffer
		global free_list
		global active_list
		global map_table
		global int_queue
		global fp_queue
		global address_queue
		global branch_stack
		global busy_bit_table

		PC = self.pc
		instr_buffer = self.instr_buffer
		free_list = self.free_list
		active_list = self.active_list
		map_table = self.map_table
		int_queue = self.int_queue
		fp_queue = self.fp_queue
		address_queue = self.address_queue
		branch_stack = self.branch_stack
		busy_bit_table = self.busy_bit_table

	def show_state(self, para):
		if para == 0:
			self.instr_buffer.display()
			self.active_list.display()
			self.int_queue.display()
			self.fp_queue.display()
			self.address_queue.display()
			self.branch_stack.display()

		elif para == 1:
			self.busy_bit_table.display()
			self.branch_stack.display()
			self.instr_buffer.display()
			self.active_list.display()
			self.int_queue.display()
			self.fp_queue.display()
			self.address_queue.display()
		
		elif para == 2:
			self.free_list.display()
			self.map_table.display()
			self.busy_bit_table.display()
			self.branch_stack.display()
			self.instr_buffer.display()
			self.active_list.display()
			self.int_queue.display()
			self.fp_queue.display()
			self.address_queue.display()
			
		else:
			print(self.pc)
			#self.busy_bit_table.display()
			self.map_table.display()
			self.branch_stack.display()
			self.instr_buffer.display()
			self.active_list.display()
			self.int_queue.display()
			self.fp_queue.display()
			self.address_queue.display()

class Pipe:
	def __init__(self, PC, instr_type):
		self.PC = PC
		self.instr_type = instr_type
		self.fetch = -1
		self.decode = -1
		self.issue = -1
		self.execute_s = -1
		self.execute_f = -1
		self.commit = -1

class Pipeline:
	def __init__(self):
		self.items = []

	def set_fetch(self, pc, x):
		for e, i in enumerate(self.items):
			if i.PC == pc :
				tpc = e 

		if self.items[tpc] :
			self.items[tpc].fetch = x

	def set_decode(self, pc, x):
		for e, i in enumerate(self.items):
			if i.PC == pc :
				tpc = e 
		if self.items[tpc] :
			self.items[tpc].decode = x

	def set_issue(self, pc, x):
		for e, i in enumerate(self.items):
			if i.PC == pc :
				tpc = e		
		if self.items[tpc] :
			self.items[tpc].issue = x

	def set_execute_s(self, pc, x):
		for e, i in enumerate(self.items):
			if i.PC == pc :
				tpc = e 		
		if self.items[tpc] :
			self.items[tpc].execute_s = x

	def set_execute_f(self, pc, x):
		for e, i in enumerate(self.items):
			if i.PC == pc :
				tpc = e 
		if self.items[tpc] :
			self.items[tpc].execute_f = x

	def set_commit(self, pc, x):
		for e, i in enumerate(self.items):
			if i.PC == pc :
				tpc = e 
		if self.items[tpc] :
			self.items[tpc].commit = x

def snapshot(cur):
	return MachineState(cur.pc, cur.instr_buffer, cur.free_list, cur.active_list, cur.map_table, cur.int_queue, cur.fp_queue, cur.address_queue, cur.branch_stack, cur.busy_bit_table)

def trace_branch(tPC):
	for i,e in enumerate(branch_stack.items) :
		if e != None and tPC == e[0] :
			return i
	return -1

def mem_disam(instr):
	for i in active_list.items :
		if i != None :
			if i.instr_type == 'S' and i.extra == instr.extra :
				if int(i.pc) < int(instr.pc) :
					return True
	return False

def display_pipeline():
	print('Instr PC, Instr Type')
	for P in pipeline.items :
		
		print(P.PC, P.instr_type, P.fetch, P.decode, P.issue, P.execute_s, P.execute_f, P.commit )

instr_buffer = Queue(8, 'Instruction Buffer')
free_list = Queue(32, 'Free List')
PC = 1
trace = []
active_list = Table(32, 'Active List')
map_table = Table(32, 'Register Map Table')
int_queue = Table(16, 'Integer Queue')
fp_queue = Table(16, 'Floating Point Queue')
address_queue = Table(16, 'Address Queue')
branch_stack = Table(4, 'Branch Stack')
busy_bit_table = Table(64, 'Busy Bit Table')
cur_state = MachineState(PC, instr_buffer, free_list, active_list, map_table, int_queue, fp_queue, address_queue, branch_stack, busy_bit_table)

pipeline = Pipeline()