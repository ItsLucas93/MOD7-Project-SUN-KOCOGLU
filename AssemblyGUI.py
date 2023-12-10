import tkinter as tk
from tkinter import filedialog, messagebox
from Assembly import Architecture

class AssemblySimulatorUI:
    def __init__(self, master):
        """
        Initialize the UI
        :param master: Tkinter master
        """
        self.master = master
        self.master.title("Assembly Simulator")
        self.architecture = Architecture()

        # File Info Frame
        file_info_frame = tk.LabelFrame(master, text="File Info", padx=5, pady=5)
        file_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(file_info_frame, text="File Name").pack()
        self.file_name_entry = tk.Entry(file_info_frame)
        self.file_name_entry.pack(fill="x", expand=True)

        tk.Label(file_info_frame, text="Code").pack()
        self.code_text = tk.Text(file_info_frame, height=10)
        self.code_text.pack(fill="both", expand=True)
        self.code_text.tag_configure('highlight', background='grey')
        self.code_text.config(state=tk.DISABLED)

        tk.Label(file_info_frame, text="Next Instruction").pack()
        self.next_instruction_entry = tk.Entry(file_info_frame, state='readonly')
        self.next_instruction_entry.pack(fill="x", expand=True)

        # Memory Info Frame
        memory_info_frame = tk.LabelFrame(master, text="Memory Info", padx=5, pady=5)
        memory_info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(memory_info_frame, text="Variables").pack()
        self.variables_text = tk.Text(memory_info_frame, height=5)
        self.variables_text.pack(fill="x", expand=True)
        for variable in self.architecture.ptr_memory:
            self.variables_text.insert(tk.END, f"{variable}: {int(self.architecture.memory[int(self.architecture.ptr_memory[variable], 2)], 2)}\n")

        tk.Label(memory_info_frame, text="Stack").pack()
        self.stack_text = tk.Text(memory_info_frame, height=5)
        self.stack_text.pack(fill="x", expand=True)
        for value in reversed(self.architecture.stack):
            self.stack_text.insert(tk.END, f"{int(value, 2)}\n")

        # Registers Frame
        registers_frame = tk.LabelFrame(master, text="Registers", padx=5, pady=5)
        registers_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.registers_text = tk.Text(registers_frame, height=5)
        self.registers_text.pack(fill="both", expand=True)
        for register in self.architecture.registers:
            self.registers_text.insert(tk.END, f"{register}: {int(self.architecture.registers[register], 2)}\n")
        self.registers_text.insert(tk.END, f"PC: {self.architecture.program_counter}\n")
        self.registers_text.config(state=tk.DISABLED)

        # Buttons Frame
        buttons_frame = tk.Frame(master)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.load_button = tk.Button(buttons_frame, text="Load File", command=self.load_file)
        self.load_button.pack(side="left", padx=5)
        self.simulate_button = tk.Button(buttons_frame, text="Simulate", command=self.simulate)
        self.simulate_button.pack(side="left", padx=5)
        self.step_button = tk.Button(buttons_frame, text="Step Simulation", command=self.step_simulation)
        self.step_button.pack(side="left", padx=5)
        self.simulate_button.config(state='disabled')
        self.step_button.config(state='disabled')

    def load_file(self):
        """
        Load a file from the user's computer (via filedialog)
        Update all the displays
        """
        self.architecture.clear_memory()
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.architecture.fetch_data(file_path)
                self.file_name_entry.delete(0, tk.END)
                self.file_name_entry.insert(0, file_path)
                self.file_name_entry.config(state='readonly')

                # Enable the widget, insert content, then disable it
                self.code_text.config(state=tk.NORMAL)  # Enable the text widget before inserting
                self.code_text.delete('1.0', tk.END)
                # To update the content

                for instruction in self.architecture.memory_code:
                    print(instruction)
                    self.code_text.insert('999.0', self.translate(instruction))

                self.code_text.config(state=tk.DISABLED)  # Disable the text widget after inserting
                self.simulate_button.config(state='normal')
                self.step_button.config(state='normal')

                next_instruction = self.translate(self.architecture.memory_code[self.architecture.program_counter])

                self.next_instruction_entry.config(state=tk.NORMAL)  # Allow writing
                self.next_instruction_entry.delete(0, tk.END)
                self.next_instruction_entry.insert(0, next_instruction)
                self.next_instruction_entry.config(state='readonly')  # Prevent further editing

                self.update_registers_display()
                self.update_stack_display()
                self.update_memory_display()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def translate(self, instruction):
        """
        Translate the instruction into a human-readable format
        :param instruction: Instruction to translate
        :return: String containing the translated instruction
        """
        if instruction['param_type_1'] == "memory":
            instruction = self.give_address_memory(instruction, 1)
        elif instruction['param_type_1'] == "register":
            instruction = self.give_address_register(instruction, 1)

        if instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
        elif instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)

        match instruction['op_code']:
            case "LDA":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "STR":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "PUSH":
                return instruction['op_code'] + " " + instruction['operand_1'] + "\n"
            case "AND":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "OR":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "ADD":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "SUB":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "DIV":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "MUL":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "MOD":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + "\n"
            case "INC":
                return instruction['op_code'] + " " + instruction['operand_1'] + "\n"
            case "DEC":
                return instruction['op_code'] + " " + instruction['operand_1'] + "\n"
            case "BEQ":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label'] + "\n"
            case "BNE":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label'] + "\n"
            case "BBG":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label'] + "\n"
            case "BSM":
                return instruction['op_code'] + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label'] + "\n"
            case "JMP":
                return instruction['op_code'] + " " + instruction['label'] + "\n"
            case "HLT":
                return instruction['op_code'] + "\n"
            case "POP":
                return instruction['op_code'] + " " + instruction['operand_1'] + "\n"
            case "NOT":
                return instruction['op_code'] + " " + instruction['operand_1'] + "\n"
            case "VAD":
                string = instruction['operand_1'][2:] + instruction['operand_2'] + instruction['label']
                string = chr(int("0b0" + string[0:7], 2)) + chr(int("0b0" + string[7:14], 2)) + chr(
                    int("0b0" + string[14:21], 2))
                return instruction['op_code'] + " " + string + "\n"
            case "VDE":
                string = instruction['operand_1'][2:] + instruction['operand_2'] + instruction['label']
                string = chr(int("0b0" + string[0:7], 2)) + chr(int("0b0" + string[7:14], 2)) + chr(
                    int("0b0" + string[14:21], 2))
                return instruction['op_code'] + " " + string + "\n"
            case _: raise ValueError("Invalid op code")


    def update_registers_display(self):
        """
        Update the registers display
        """
        # Clear the current content of the register display
        self.registers_text.config(state=tk.NORMAL)  # Enable text widget for editing
        self.registers_text.delete('1.0', tk.END)

        # Insert the updated register values
        for register in self.architecture.registers:
            self.registers_text.insert(tk.END, f"{register}: {int(self.architecture.registers[register], 2)}\n")
        self.registers_text.insert(tk.END, f"PC: {self.architecture.program_counter}\n")

        self.registers_text.config(state=tk.DISABLED)  # Disable text widget to prevent editing

    def update_memory_display(self):
        """
        Update the memory display
        """
        self.variables_text.config(state=tk.NORMAL)  # Enable text widget for editing
        self.variables_text.delete('1.0', tk.END)
        for variable in self.architecture.ptr_memory:
            self.variables_text.insert(tk.END, f"{variable}: {int(self.architecture.memory[int(self.architecture.ptr_memory[variable], 2)], 2)}\n")
        self.variables_text.config(state=tk.DISABLED)  # Disable text widget to prevent editing

    def update_stack_display(self):
        """
        Update the stack display
        """
        self.stack_text.config(state=tk.NORMAL)  # Enable text widget for editing
        self.stack_text.delete('1.0', tk.END)
        # Insert the updated stack values in reversed order
        for value in reversed(self.architecture.stack):
            self.stack_text.insert(tk.END, f"{int(value, 2)}\n")
        self.stack_text.config(state=tk.DISABLED)  # Disable text widget to prevent editing

    def clear_highlight(self):
        """
        Clear the highlight from the code display
        """
        self.code_text.tag_remove('highlight', '1.0', tk.END)

    def apply_highlight(self, line_number):
        """
        Apply highlight to the code display
        :param line_number: Line number to highlight (Provided by the PC)
        """
        self.code_text.tag_add('highlight', f"{line_number}.0", f"{line_number}.end")

    def simulate(self):
        """
        Simulate the program with Simulation button
        """
        self.clear_highlight()
        # Implement simulation functionality
        result = self.architecture.execute_program("full")
        if result == "END":
            self.simulate_button.config(state='disabled')
            self.step_button.config(state='disabled')
        self.update_registers_display()
        self.update_memory_display()
        self.update_stack_display()
        current_line = self.architecture.program_counter + 1
        self.apply_highlight(current_line)

    def step_simulation(self):
        """
        Simulate the program step-by-step with Step Simulation button
        """
        self.clear_highlight()
        # Implement step simulation functionality
        result = self.architecture.execute_program("step")
        self.simulate_button.config(state='disabled')
        if result == "END":
            self.step_button.config(state='disabled')
            next_instruction = ""
        else:
            next_instruction = self.translate(self.architecture.memory_code[self.architecture.program_counter])

        # Update code display if VAD or VDE
        print(result)
        if result == "VAD" or result == "VDE":
            self.code_text.config(state=tk.NORMAL)
            self.code_text.delete('1.0', tk.END)
            for instruction in self.architecture.memory_code:
                self.code_text.insert('999.0', self.translate(instruction))
            self.code_text.config(state=tk.DISABLED)
        # Update next instruction display
        self.next_instruction_entry.config(state=tk.NORMAL)  # Allow writing
        self.next_instruction_entry.delete(0, tk.END)
        self.next_instruction_entry.insert(0, next_instruction)
        self.next_instruction_entry.config(state='readonly')  # Prevent further editing
        self.update_registers_display()
        self.update_memory_display()
        self.update_stack_display()
        current_line = self.architecture.program_counter + 1
        self.apply_highlight(current_line)

    def give_address_memory(self, instruction, param_number):
        """
        Give the address of the memory location
        :param instruction: Instruction containing the memory location
        :param param_number: Which param to give the address of
        :return: Instruction with the address of the memory location
        """
        match param_number:
            case 1:
                index_param = 'param_type_1'
                index_operand = 'operand_1'
            case 2:
                index_param = 'param_type_2'
                index_operand = 'operand_2'
            case _: raise ValueError("Invalid param number")

        if instruction[index_param] == "memory":
            try:
                # Get variable name from pointer memory
                for key, value in self.architecture.ptr_memory.items():
                    if value == instruction[index_operand] or key == instruction[index_operand]:
                        instruction[index_operand] = key
                        return instruction
            except IndexError:
                raise ValueError("Invalid memory position")
            # instruction[index_operand] = "???"
            return instruction
        raise ValueError("Invalid param type")

    def give_address_register(self, instruction, param_number):
        match param_number:
            case 1:
                index_param = 'param_type_1'
                index_operand = 'operand_1'
            case 2:
                index_param = 'param_type_2'
                index_operand = 'operand_2'
            case _: raise ValueError("Invalid param number")

        if instruction[index_param] == "register":
            match instruction[index_operand]:
                case "000000000" | "t0": instruction[index_operand] = "t0"
                case "000000001" | "t1": instruction[index_operand] = "t1"
                case "000000010" | "t2": instruction[index_operand] = "t2"
                case "000000011" | "t3": instruction[index_operand] = "t3"
                case _: raise ValueError("Invalid register")
            return instruction
        raise ValueError("Invalid param type")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblySimulatorUI(root)
    root.mainloop()
