

path = "C:\\Users\\smuzi\\Documents\\GitHub\\bnhailfinder\\hailfinder.bif"
count = 0
with open(path) as f:
    for line in f:
        if '|' in line:
            count += 1
            splitline = line.split(' ')
            child = splitline[2]
            line_length = len(splitline)
            if (line_length==7): #minline: probability ( child | parent ) {
                parent = [splitline[4]]
            else:
                parent = []
                for i in range(4,line_length-2):
                    parent.append(splitline[i])

            print "node: "+str(child)+" parent(s): "+' '.join(parent)
    print count