import globals
import sys
import time

row_deli = "\n"
col_deli = ",\t"
out_ext = ".csv"
plt_ext = ".pdf"
con_ext = ".con"

RESULT_DIR = "result/"


def output_file_name():
    # result directory
    result_file = RESULT_DIR

    # add arguments
    if len(sys.argv) <= 1:
        return ""

    file_name = sys.argv[1]
    if '/' in file_name:
        file_name = file_name[file_name.rfind('/')+1:]
    if file_name[len(con_ext)*-1:] == con_ext:
        file_name = file_name[:-4]

    result_file += file_name
    for i in range(2, len(sys.argv), 2):
        result_file += sys.argv[i]+"_"+sys.argv[i+1]

    # add timestamp
    t0 = time.localtime()
    result_file += str(t0.tm_yday) + "_" + str(t0.tm_hour) + "_" + str(t0.tm_min) + "_" + str(t0.tm_sec)

    return result_file


def element_output(*contents):
    result = str(contents[0])
    for c in contents[1:]:
        result += col_deli + str(c)
    return result


def result_file_format(appr=globals.Approach):
    result = ""
    result += element_output("TestFile", "ConNum", "ParttAlg")
    for app in appr:
        result += col_deli + appr[app]
    return result


def store_result_file(file_no_ext, test_file_name, num, partt_alg, perform, appr=globals.Approach):
    out = open(file_no_ext + out_ext, 'w')
    out.write(result_file_format()+row_deli)
    for i in range(0, len(test_file_name)):
        out.write(element_output(test_file_name[i], num[i], partt_alg[i]))
        for app in appr:
            out.write(col_deli+str((perform[app])[i]))
        out.write(row_deli)
    out.close()


def read_result_file(input_file):
    in_file = open(input_file, 'r')
    input_str = in_file.read()
    in_file.close()

    files = []
    number = []
    partt_alg = []
    perform = {}
    lines = input_str.split(row_deli)
    # if lines[0] != result_file_format():
    #     return None
    elements = lines[0].split(col_deli)
    index = []
    for ele in elements[3:]:
        for app in globals.Approach:
            if ele==globals.Approach[app]:
                index.append(app)
                perform[app] = []

    for line in lines[1:]:
        elements = line.split(col_deli)
        if len(elements) > 3:
            files.append(elements[0])
            number.append(int(elements[1]))
            partt_alg.append(int(elements[2]))
            for i in range(0, len(index)):
                perform[index[i]].append(float(elements[i+3]))

    return files, number, partt_alg, perform


# if __name__ == '__main__':
#     files, number, partt_alg, perform = read_result_file("result/simple322_23_8_58.out")
