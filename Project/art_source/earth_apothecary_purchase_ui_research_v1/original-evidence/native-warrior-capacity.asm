
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

00593085 <.text+0x192085>:
  593085:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  59308b:	be 19 00 00 00       	mov    esi,0x19
  593090:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  593097:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  59309a:	8b c8                	mov    ecx,eax
  59309c:	c1 e1 05             	shl    ecx,0x5
  59309f:	2b c8                	sub    ecx,eax
  5930a1:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  5930a4:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  5930a7:	8d 04 88             	lea    eax,[eax+ecx*4]
  5930aa:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  5930ad:	66 89 b4 81 ea 1f 00 	mov    WORD PTR [ecx+eax*4+0x1fea],si
  5930b4:	00 
  5930b5:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  5930bb:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  5930c2:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  5930c5:	8b c8                	mov    ecx,eax
  5930c7:	c1 e1 05             	shl    ecx,0x5
  5930ca:	2b c8                	sub    ecx,eax
  5930cc:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  5930cf:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  5930d2:	8d 04 88             	lea    eax,[eax+ecx*4]
  5930d5:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  5930d8:	66 c7 84 81 ee 1f 00 	mov    WORD PTR [ecx+eax*4+0x1fee],0x5
  5930df:	00 05 00 
  5930e2:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  5930e8:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  5930ef:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  5930f2:	8b c8                	mov    ecx,eax
  5930f4:	c1 e1 05             	shl    ecx,0x5
  5930f7:	2b c8                	sub    ecx,eax
  5930f9:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  5930fc:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  5930ff:	8d 04 88             	lea    eax,[eax+ecx*4]
  593102:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  593105:	66 89 b4 81 80 20 00 	mov    WORD PTR [ecx+eax*4+0x2080],si
  59310c:	00 
