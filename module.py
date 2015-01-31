import utils as U
import structures as DS
import pdb
#import sys
#sys.stdout = open('output.txt','w')
def widget_calc(i):
	U.fetch_calc(i)
	U.decode_calc(i)
	U.issue_calc(i)

	U.alu1_calc(i+1)
	U.alu2_calc(i+1)

	U.ls1a_calc(i+1)
	U.ls1b_calc(i+1)
	
	U.fpA1a_calc(i+1)
	U.fpA1b_calc(i+1)
	U.fpA1c_calc(i+1)
	
	U.fpM1a_calc(i+1)
	U.fpM1b_calc(i+1)
	U.fpM1c_calc(i+1)
	
	U.commit_calc(i+1)

def widget_edge(i):
	U.fetch_edge(i)
	U.decode_edge(i)
	U.issue_edge(i)
	
	U.alu1_edge(i+1)
	U.alu2_edge(i+1)

	U.ls1a_edge(i+1)
	U.ls1b_edge(i+1)
	
	U.fpA1a_edge(i+1)
	U.fpA1b_edge(i+1)
	U.fpA1c_edge(i+1)
	
	U.fpM1a_edge(i+1)
	U.fpM1b_edge(i+1)
	U.fpM1c_edge(i+1)
	
	U.commit_edge(i+1)

def main():
	U.boot()
	num_cycles = 200

	for i in range(num_cycles):
		#print('________Cycle = ', i,'______')
		DS.cur_state.update_state()
		#DS.cur_state.show_state(0)
		#print()
		widget_calc(i)
		widget_edge(i)
	DS.display_pipeline()
main()
#sys.stdout.close()