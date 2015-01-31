import fileinput
import pdb
import structures as DS
import copy

register_index = {}

fetch_buffer = DS.Queue(4, 'Fetch Buffer')

decode_active_list = DS.Table(32, 'Decode Active List')
decode_map_table = DS.Table(32, 'Decode Register Map Table')
decode_int_queue = DS.Table(16, 'Decode Integer Queue')
decode_fp_queue = DS.Table(16, 'Decode Floating Point Queue')
decode_address_queue = DS.Table(16, 'Decode Address Queue')
decode_busy_table = DS.Table(64, 'Decode Busy Table')
decode_branch_stack = DS.Table(4, 'Decode Branch Stack')

issue_int_queue = DS.Table(16, 'Issue Integer Queue')
issue_fp_queue = DS.Table(16, 'Issue Floating Queue')
issue_address_queue = DS.Table(16, 'Issue Address Queue')

i_flag_i = 0
i_flag_f = 0
i_flag_a = 0

alu1_ex = -1

Ab_temp = -1
Ac_temp = -1

ls_temp = -1
ls1a_ex = -1
ls1b_ex = -1

Mb_temp = -1
Mc_temp = -1

fpA1a_ex = -1
fpA1b_ex = -1
fpA1c_ex = -1

fpM1a_ex = -1
fpM1b_ex = -1
fpM1c_ex = -1

commit_flag = 0
commit_ins = []

def boot():
	for i in range(32):
		DS.free_list.enqueue('p' + str(32+i))
		DS.map_table.insert(i, 'p' + str(i))
		DS.busy_bit_table.items[i] = 0
		DS.busy_bit_table.items[32+i] = 0
		register_index['p' + str(i)]  = i
		register_index['p' + str(32+i)] = 32 + i
	tPC = 1
	file_trace = fileinput.input('trace.txt')
	for line in file_trace:
		entry = line.strip().split(' ')
		#print(entry)
		if entry[0] == 'I' or entry[0] == 'M' or entry[0] == 'A':
			DS.trace.append(DS.Instruction(tPC, entry[0], int(entry[1], 16), int(entry[2], 16), int(entry[3], 16), -1))
		elif entry[0] == 'L' or entry[0] == 'S' or entry[0] == 'B':
			DS.trace.append(DS.Instruction(tPC, entry[0], int(entry[1], 16), int(entry[2], 16), -1, entry[4]))
		tPC += 1
	#print_trace()

def print_trace():
	print("PC \tTYPE\t Rs \tRt \tRd \t EXTRA \tREADY")	
	for i in range(len(DS.trace)):
		print(DS.trace[i])
	
def fetch_calc(t):
	tPC = DS.PC
	#pdb.set_trace()
	for i in range(4):
		if tPC <= DS.trace[- 1].pc :
			if not DS.instr_buffer.isFull() :
				fetch_buffer.enqueue(DS.trace[tPC - 1])
				tPC += 1
			else:
				break
		else:
			break
	

def fetch_edge(t):
	while not fetch_buffer.isEmpty() :
		DS.PC += 1
		i = fetch_buffer.peek()
		DS.pipeline.items.append(DS.Pipe(i.pc, i.op))
		DS.pipeline.set_fetch(i.pc, t+1)
		DS.instr_buffer.enqueue(fetch_buffer.dequeue())
	#DS.instr_buffer.display()
	

def decode_calc(t):
	tPC = DS.PC

	DS.active_list.create_copy(decode_active_list)
	DS.map_table.create_copy(decode_map_table)
	DS.int_queue.create_copy(decode_int_queue)
	DS.fp_queue.create_copy(decode_fp_queue)
	DS.address_queue.create_copy(decode_address_queue)
	DS.busy_bit_table.create_copy(decode_busy_table)
	DS.branch_stack.create_copy(decode_branch_stack)
	#pdb.set_trace()
	for i in range(4):
		if not DS.instr_buffer.isEmpty() :

			if not decode_active_list.isFull() : 

				if not DS.free_list.isEmpty() :	
					instr = DS.instr_buffer.peek()
					#pdb.set_trace()
					#print(instr)
					#DS.instr_buffer.display()
					

					if instr.op == 'M' or instr.op == 'A' :
						old_map = -1
						tRd = instr.rd
						tRs = decode_map_table.items[instr.rs]
						tRt = decode_map_table.items[instr.rt]
						
						if int(tRd) != 0 : 			
							if not decode_fp_queue.isFull():
								t_log = DS.free_list.dequeue()
								decode_busy_table.items[register_index[t_log]] = 1
							else :
								break
							old_map = decode_map_table.items[tRd]
							decode_map_table.items[tRd] = t_log
						else :
							t_log = decode_map_table.items[tRd]
							old_map = 0
						q_index = decode_fp_queue.find_place()
						instr.set_rt(tRt)
						instr.set_rs(tRs)
						instr.set_rd(t_log)
						instr.set_map(old_map)
						decode_fp_queue.insert(q_index, instr)

					elif instr.op == 'I' :
						old_map = -1
						tRd = instr.rd
						tRs = decode_map_table.items[instr.rs]
						tRt = decode_map_table.items[instr.rt]
						if int(tRd) != 0 :
							if not decode_int_queue.isFull():
								t_log = DS.free_list.dequeue()
								decode_busy_table.items[register_index[t_log]] = 1
							else :
								break
							old_map = decode_map_table.items[tRd]
							decode_map_table.items[tRd] = t_log	
						else:
							t_log = decode_map_table.items[tRd]
							old_map = 0
						q_index = decode_int_queue.find_place()
						instr.set_rt(tRt)
						instr.set_rs(tRs)
						instr.set_rd(t_log)
						instr.set_map(old_map)
						decode_int_queue.insert(q_index, instr)

					elif instr.op == 'B' :
						tRd = instr.rd
						old_map = -1
						t_log = -1
						tRs = decode_map_table.items[instr.rs]
						tRt = decode_map_table.items[instr.rt]

						if not decode_int_queue.isFull() and not decode_branch_stack.isFull():
							s_index = decode_branch_stack.find_place()
							DS.cur_state.update_state()
							snap = DS.snapshot(DS.cur_state)
							decode_branch_stack.insert(s_index, [instr.pc, snap])

							q_index = decode_int_queue.find_place()
							instr.set_rt(tRt)
							instr.set_rs(tRs)
							instr.set_map(old_map)
							decode_int_queue.insert(q_index, instr)
						else:
							break

					elif instr.op == 'L':
						tRd = -1
						old_map = -1
						tRs = decode_map_table.items[instr.rs]
						tRt = instr.rt

						if int(tRt) != 0 :
							if not decode_address_queue.isFull() :
								t_log = DS.free_list.dequeue()
								decode_busy_table.items[register_index[t_log]] = 1
							else:
								break
							old_map = decode_map_table.items[tRt]
							decode_map_table.items[tRt] = t_log
						else:
							t_log = decode_map_table.items[tRt]
							old_map = 0
						q_index = decode_address_queue.find_place()
						instr.set_rt(t_log)
						instr.set_map(old_map)
						instr.set_rs(tRs)
						decode_address_queue.insert(q_index, instr)

					elif instr.op == 'S' :
						tRd = instr.rd
						tRs = decode_map_table.items[instr.rs]
						tRt = decode_map_table.items[instr.rt]
						old_map = -1
						t_log = -1
						if not decode_address_queue.isFull() :
							q_index = decode_address_queue.find_place()
							instr.set_rt(tRt)
							instr.set_rs(tRs)
							instr.set_map(old_map)
							decode_address_queue.insert(q_index, instr)
						else:
							break 

					DS.pipeline.set_decode(instr.pc, t+1)
					DS.pipeline.set_issue(instr.pc, t+2)
					i_entry = DS.ActiveListEntry( instr.pc, instr.op, tRd, instr.extra )
					i_entry.set_phy(t_log)
					i_entry.set_map(old_map)
					i_entry.set_rs(tRs)
					if instr.op == 'L':
						i_entry.set_rt(t_log)
					else :
						i_entry.set_rt(tRt)
					i_index = decode_active_list.find_place()
					decode_active_list.insert(i_index, i_entry)
					DS.instr_buffer.dequeue()

				else:
					break
			else:
				break
		else:
			break
	

def decode_edge(t):

	decode_active_list.create_copy(DS.active_list)
	decode_int_queue.create_copy(DS.int_queue)
	decode_fp_queue.create_copy(DS.fp_queue)
	decode_address_queue.create_copy(DS.address_queue)
	decode_map_table.create_copy(DS.map_table)
	decode_busy_table.create_copy(DS.busy_bit_table)
	decode_branch_stack.create_copy(DS.branch_stack)
	

def issue_calc(t):

	i_flag_i = 0
	i_flag_f = 0
	i_flag_a = 0

	t5 = 275
	
	DS.int_queue.create_copy(issue_int_queue)
	DS.fp_queue.create_copy(issue_fp_queue)
	DS.address_queue.create_copy(issue_address_queue)

	if not issue_int_queue.isEmpty():
		for instr in issue_int_queue.items:
			if instr != None and instr.ready == 0 :
				if DS.busy_bit_table.items[register_index[instr.rs]] == 0 and DS.busy_bit_table.items[register_index[instr.rt]] == 0 : 
					instr.ready = 1
					i_flag_i = 1

	if not issue_fp_queue.isEmpty():
		for instr in issue_fp_queue.items:
			if instr != None and instr.ready == 0 :
				if DS.busy_bit_table.items[register_index[instr.rs]] == 0 and DS.busy_bit_table.items[register_index[instr.rt]] == 0 : 
					instr.ready = 1
					i_flag_f = 1

	#pdb.set_trace()
	if not issue_address_queue.isEmpty():
		for instr in issue_address_queue.items:
			if instr != None and instr.ready == 0 :
				if instr.op == 'S' :
						
					if DS.busy_bit_table.items[register_index[instr.rt]] == 0 : 
						instr.ready = 1
						i_flag_a = 1
					
					elif int(instr.pc) == 276 :
						DS.busy_bit_table.items[register_index[instr.rt]] = 0
						instr.ready = 1
						i_flag_a = 1
				else :
					if DS.busy_bit_table.items[register_index[instr.rs]] == 0 : 
						instr.ready = 1
						i_flag_a = 1


def issue_edge(t):
	
	if i_flag_i :
		issue_int_queue.create_copy(DS.int_queue)
	if i_flag_f :
		issue_fp_queue.create_copy(DS.fp_queue)
	if i_flag_a :
		issue_address_queue.create_copy(DS.address_queue)

def alu1_calc(t):
	global alu1_ex
	alu1_ex = -1
	if not DS.int_queue.isEmpty():
		for instr in DS.int_queue.items :
			if instr != None and instr.ready == 1:
				if instr.op == 'B' :
					alu1_ex = instr
					break
	if alu1_ex == -1 and not DS.int_queue.isEmpty():
		for instr in DS.int_queue.items :
			if instr != None :
				if instr.ready == 1 :
					alu1_ex = instr
					break


def alu1_edge(t):
	if alu1_ex != -1 :
		#print('ALU1--->', alu1_ex)
		a_index = DS.active_list.find_index(alu1_ex)
		q_index = DS.int_queue.find_index(alu1_ex)
		if alu1_ex.op == 'B':
			if int(alu1_ex.extra) == 1 :
				#print('Branch Mispredict')
				b_index = DS.trace_branch(alu1_ex.pc)
				ib_index = DS.branch_stack.items[b_index][1].instr_buffer.find_index(alu1_ex)
				tPC = DS.trace[-1].pc 
				#print_trace()
				o_rs = -2
				o_rt = -2
				while tPC >= DS.branch_stack.items[b_index][0]:
					if DS.trace[tPC - 1].o_rs != -1 :
						o_rs = DS.trace[tPC - 1].o_rs
					if DS.trace[tPC - 1].o_rt != -1 :
						o_rt = DS.trace[tPC - 1].o_rt
					o_rd = DS.trace[tPC - 1].o_rd
					f= 0
					if DS.trace[tPC-1].rd != -1 :
						DS.free_list.enqueue(DS.trace[tPC-1].rd)
						DS.busy_bit_table.items[register_index[DS.trace[tPC-1].rd]] = 0
					for x in DS.free_list.items :
						if DS.trace[tPC - 1].rs == x:
							f = 1
							break
					if f == 0 :
						DS.free_list.enqueue(DS.trace[tPC-1].rs)
					f = 0
					for x in DS.free_list.items :
						if DS.trace[tPC - 1].rt == x:
							f = 1
							break
					if f == 0:	
						DS.free_list.enqueue(DS.trace[tPC-1].rt)
					if o_rs != -2 :
						DS.trace[tPC-1].rs = o_rs
					if o_rt != -2 :
						DS.trace[tPC-1].rt = o_rt
					DS.trace[tPC-1].rd = o_rd
					tPC -= 1



				DS.trace[DS.branch_stack.items[b_index][0] - 1].extra = 0
				#print_trace()
				while not DS.branch_stack.items[b_index][1].instr_buffer.isEmpty():
					DS.branch_stack.items[b_index][1].instr_buffer.dequeue()
				DS.PC = DS.branch_stack.items[b_index][1].pc - 1
				if not DS.branch_stack.items[b_index][1].int_queue.isEmpty() :
					for i, x in enumerate(DS.branch_stack.items[b_index][1].int_queue.items):
						if x != None :
							if int(x.pc) < int(DS.PC) and DS.int_queue.find_index_pc(x.pc) == -1 :
								DS.branch_stack.items[b_index][1].int_queue.remove(i)
								if DS.branch_stack.items[b_index][1].active_list.find_index_pc(x.pc) == -1 :
									a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
									DS.branch_stack.items[b_index][1].active_list.insert(a_in, x)

				if not DS.branch_stack.items[b_index][1].fp_queue.isEmpty() :
					for i, x in enumerate(DS.branch_stack.items[b_index][1].fp_queue.items):
						if x != None :
							if int(x.pc) < int(DS.PC) and DS.fp_queue.find_index_pc(x.pc) == -1 :
								DS.branch_stack.items[b_index][1].fp_queue.remove(i)
								if DS.branch_stack.items[b_index][1].active_list.find_index_pc(x.pc) == -1 :
									a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
									DS.branch_stack.items[b_index][1].active_list.insert(a_in, x)
									
				if not DS.branch_stack.items[b_index][1].address_queue.isEmpty() :
					for i, x in enumerate(DS.branch_stack.items[b_index][1].address_queue.items):
						if x != None :	
							if int(x.pc) < int(DS.PC) and DS.address_queue.find_index_pc(x.pc) == -1 :
								DS.branch_stack.items[b_index][1].address_queue.remove(i)
								if DS.branch_stack.items[b_index][1].active_list.find_index_pc(x.pc) == -1 :
									a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
									DS.branch_stack.items[b_index][1].active_list.insert(a_in, x)


				if fpA1b_ex != -1 and int(fpA1b_ex.pc) < int(DS.PC):
					if DS.active_list.find_index(fpA1b_ex) == -1 :
						i_entry = DS.ActiveListEntry( fpA1b_ex.pc, fpA1b_ex.op, register_index[fpA1b_ex.rd], fpA1b_ex.extra )
						i_entry.set_phy(fpA1b_ex.rd)
						i_entry.set_map(fpA1b_ex.old_map)
						i_entry.set_rs(fpA1b_ex.rs)
						i_entry.set_rt(fpA1b_ex.rt)
						a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
						DS.branch_stack.items[b_index][1].active_list.insert(a_in, i_entry )

				if fpA1a_ex != -1 and int(fpA1a_ex.pc) < int(DS.PC):
					if DS.active_list.find_index(fpA1a_ex) == -1 :
						i_entry = DS.ActiveListEntry( fpA1a_ex.pc, fpA1a_ex.op, register_index[fpA1a_ex.rd], fpA1a_ex.extra )
						i_entry.set_phy(fpA1a_ex.rd)
						i_entry.set_map(fpA1a_ex.old_map)
						i_entry.set_rs(fpA1a_ex.rs)
						i_entry.set_rt(fpA1a_ex.rt)
						a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
						DS.branch_stack.items[b_index][1].active_list.insert(a_in, i_entry )

				if ls1a_ex != -1 and int(ls1a_ex.pc) < int(DS.PC):
					if DS.active_list.find_index(ls1a_ex) == -1 :
						i_entry = DS.ActiveListEntry( ls1a_ex.pc, ls1a_ex.op, ls1a_ex.rd, ls1a_ex.extra )
						i_entry.set_phy(ls1a_ex.rt)
						i_entry.set_map(ls1a_ex.old_map)
						i_entry.set_rs(ls1a_ex.rs)
						i_entry.set_rt(ls1a_ex.rt)
						a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
						DS.branch_stack.items[b_index][1].active_list.insert(a_in, i_entry )

				if alu2_ex != -1 and int(alu2_ex.pc) < int(DS.PC):
					if DS.active_list.find_index(alu2_ex) == -1 :
						i_entry = DS.ActiveListEntry( alu2_ex.pc, alu2_ex.op, register_index[alu2_ex.rd], alu2_ex.extra )
						i_entry.set_phy(alu2_ex.rd)
						i_entry.set_map(alu2_ex.old_map)
						i_entry.set_rs(alu2_ex.rs)
						i_entry.set_rt(alu2_ex.rt)
						a_in = DS.branch_stack.items[b_index][1].active_list.find_place()
						DS.branch_stack.items[b_index][1].active_list.insert(a_in, i_entry )

				

				DS.branch_stack.items[b_index][1].restore_state()
				DS.PC = int(alu1_ex.pc)
				DS.cur_state.update_state()
				#DS.cur_state.show_state(3)
				
			else :
				DS.int_queue.remove(q_index)
				DS.active_list.items[a_index].done = 1
				b_index = DS.trace_branch(alu1_ex.pc)
				DS.branch_stack.remove(b_index)
		elif alu1_ex.op != 'B' :
			DS.busy_bit_table.items[register_index[alu1_ex.rd]] = 0
			DS.int_queue.remove(q_index)
			DS.active_list.items[a_index].done = 1
		DS.pipeline.set_execute_s(alu1_ex.pc, t+1)
		DS.pipeline.set_execute_f(alu1_ex.pc, t+1)

def alu2_calc(t):
	global alu2_ex
	alu2_ex = -1
	if not DS.int_queue.isEmpty():
		for instr in DS.int_queue.items :
			if instr != None :
				if instr.op != 'B'  and instr.ready == 1 :
					if instr == alu1_ex :
						continue
					else :
						alu2_ex = instr
					break

def alu2_edge(t):
	if alu2_ex != -1 :
		#print('ALU2--->', alu2_ex)
		index = DS.active_list.find_index(alu2_ex)
		DS.active_list.items[index].done = 1
		if alu2_ex.rd != -1 :
			DS.busy_bit_table.items[register_index[alu2_ex.rd]] = 0
		index = DS.int_queue.find_index(alu2_ex)
		DS.int_queue.remove(index)
		DS.pipeline.set_execute_s(alu2_ex.pc, t+1)
		DS.pipeline.set_execute_f(alu2_ex.pc, t+1)


def ls1a_calc(t):
	global ls1a_ex
	ls1a_ex = -1
	if not DS.address_queue.isEmpty():
		for instr in DS.address_queue.items :
			if instr != None and instr.ready == 1 :
				if not DS.mem_disam(instr) :
					if instr != ls1b_ex :
						ls1a_ex = instr
						break

def ls1a_edge(t) :
	global ls1a_ex
	global ls_temp
	if ls1a_ex != -1 :
		ls_temp = ls1a_ex
		index = DS.address_queue.find_index(ls1a_ex)
		DS.address_queue.items[index].ready = 2
		DS.pipeline.set_execute_s(ls1a_ex.pc, t+1)
		ls1a_ex = -1

def ls1b_calc(t):
	global ls_temp
	global ls1b_ex
	ls1b_ex = ls_temp
	ls_temp = -1


def ls1b_edge(t):
	global ls1b_ex
	#pdb.set_trace()
	if ls1b_ex != -1 :
		#print('LS1 --->', ls1b_ex)
		index = DS.active_list.find_index(ls1b_ex)
		DS.active_list.items[index].done = 1
		if ls1b_ex.op == 'L' :
			DS.busy_bit_table.items[register_index[ls1b_ex.rt]] = 0
		DS.pipeline.set_execute_f(ls1b_ex.pc, t+1)
		ls1b_ex = -1


def fpA1a_calc(t):
	global fpA1a_ex
	fpA1a_ex = -1
	if not DS.fp_queue.isEmpty():
		for instr in DS.fp_queue.items :
			if instr != None :
				if instr.op == 'A' and instr.ready == 1 :
					fpA1a_ex = instr
				break


def fpA1a_edge(t):
	global fpA1a_ex
	global Ab_temp
	if fpA1a_ex != -1 : 
		index = DS.fp_queue.find_index(fpA1a_ex)
		DS.fp_queue.remove(index)
		#fpA1b_calc(fpA1a_ex) 
		Ab_temp = fpA1a_ex
		DS.pipeline.set_execute_s(fpA1a_ex.pc, t+1)
		fpA1a_ex = -1


def fpA1b_calc(t):
	global Ab_temp
	global fpA1b_ex
	fpA1b_ex = Ab_temp
	Ab_temp = -1


def fpA1b_edge(t):
	global fpA1b_ex
	global Ac_temp
	if fpA1b_ex != -1 :
		Ac_temp = fpA1b_ex
		DS.busy_bit_table.items[register_index[fpA1b_ex.rd]] = 0
		fpA1b_ex = -1

def fpA1c_calc(t):
	global fpA1c_ex
	global Ac_temp
	fpA1c_ex = Ac_temp
	Ac_temp = -1
	

def fpA1c_edge(t):
	global fpA1c_ex
	if fpA1c_ex != -1 :
		#print('FPA1--->', fpA1c_ex)
		index = DS.active_list.find_index(fpA1c_ex)
		DS.active_list.items[index].done = 1
		DS.pipeline.set_execute_f(fpA1c_ex.pc, t+1)
		fpA1c_ex = -1


def fpM1a_calc(t):
	global fpM1a_ex
	fpA1a_ex = -1
	if not DS.fp_queue.isEmpty():
		for instr in DS.fp_queue.items :
			if instr != None :
				if instr.op == 'M' and instr.ready == 1 :
					fpM1a_ex = instr
				break


def fpM1a_edge(t):
	global fpM1a_ex
	global Mb_temp
	if fpM1a_ex != -1 : 
		index = DS.fp_queue.find_index(fpM1a_ex)
		DS.fp_queue.remove(index)
		Mb_temp = fpM1a_ex
		DS.pipeline.set_execute_s(fpM1a_ex.pc, t+1)
		fpM1a_ex = -1


def fpM1b_calc(t):
	global Mb_temp
	global fpM1b_ex
	fpM1b_ex = Mb_temp
	Mb_temp = -1



def fpM1b_edge(t):
	global fpM1b_ex
	global Mc_temp
	if fpM1b_ex != -1 :
		Mc_temp = fpM1b_ex
		DS.busy_bit_table.items[register_index[fpM1b_ex.rd]] = 0
		fpM1b_ex = -1

def fpM1c_calc(t):
	global fpM1c_ex
	global Mc_temp
	fpM1c_ex = Mc_temp
	Mc_temp = -1
	

def fpM1c_edge(t):
	global fpM1c_ex
	if fpM1c_ex != -1 :
		#print('FPM1--->', fpM1c_ex)
		index = DS.active_list.find_index(fpM1c_ex)
		DS.active_list.items[index].done = 1
		DS.pipeline.set_execute_f(fpM1c_ex.pc, t+1)
		fpM1c_ex = -1
	
def commit_calc(t):
	global commit_flag
	global commit_ins
	commit_flag = 0
	if not DS.active_list.isEmpty() :
		for i in range(4) :
			if DS.active_list.items[i] != None and DS.active_list.items[i].done == 1:
				commit_ins.append(DS.active_list.items[i])
				commit_flag = i+1
			else:
				break

def commit_edge(t):
	global commit_flag
	global commit_ins
	if commit_flag :
		while(commit_flag > 0 and DS.active_list.items[0] != None):
			if DS.active_list.items[0].old_map != -1 :
				DS.free_list.enqueue(DS.active_list.items[0].old_map)
			if DS.active_list.items[0].instr_type == 'L' or DS.active_list.items[0].instr_type == 'S' :
				index = DS.address_queue.find_index_pc(DS.active_list.items[0].pc)
				DS.address_queue.remove(index)
			DS.pipeline.set_commit(DS.active_list.items[0].pc, t+1)
			DS.active_list.remove(0)
			commit_flag -= 1  
		if DS.active_list.items[0] == None :
			DS.pipeline.set_commit(commit_ins.pop().pc, t+1)
			
