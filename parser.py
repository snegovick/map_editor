import re

def strtok(s, delim):
    result = filter(None, re.split(delim, s))
    return result

class Parser:
   def __init__(self):
       self.values = {}
       
   def parse_real(self, s, name):
       print "s:",s, "name:", name
       temp = s[:s.find(";")-1]
       self.values[name] = float(temp)

   def get_real_value(self, temp):
       try:
           return float(temp)
       except:
           return None

   def get_string_value(self, temp):
       start = temp.find("\"")
       end = temp[start+1:].find("\"")
       try:
           return temp[start+1:start+end+1]
       except:
           return None
       
   def parse_array(self, s, name, typ="array"):
       print "s:",s, "name:", name
       start = s.find("{")
       end = s.find("}")
       offset = 0
       prev_str = s[start+1:end]
       values = []
       while offset<end:
           coma = prev_str.find(",")
           if coma == -1:
               temp = prev_str
               offset = end
           else:
               temp = prev_str[:coma]
               offset+=coma
           if typ == "array":
               val = self.get_real_value(temp)
           elif typ == "sarray":
               val = self.get_string_value(temp)

           if val == None:
               break

           values.append(val)
           prev_str=prev_str[coma+1:]

       #print "len:", len(values)
       #print values
       self.values[name] = values

   def parse_string(self, s, name):
       val = self.get_string_value(s)
       self.values[name] = val

   def parse(self, filename):
       f = open(filename, "r")
       buf = f.read()
       f.close()
       
       offset = 0
       buf = buf.replace("\n", "")
       
       while offset<len(buf):
           endline = buf[offset:].find(";")
           temp = buf[offset:offset+endline+1]

           print "temp:", temp
           tokens = strtok(temp, " ")
           if (tokens == []):
               break
           print "tokens:", tokens
           substr = temp[temp.find("=")+1:]
           if tokens[0] == "real":
               self.parse_real(substr, tokens[1])
           elif tokens[0] == "str":
               self.parse_string(substr, tokens[1])
           elif tokens[0] == "array":
               self.parse_array(substr, tokens[1], "array")
           elif tokens[0] == "sarray":
               self.parse_array(substr, tokens[1], "sarray")

           offset+=len(temp)

       return self.values

if __name__=="__main__":
    
    p = Parser()
    print p.parse("test.gmp")
