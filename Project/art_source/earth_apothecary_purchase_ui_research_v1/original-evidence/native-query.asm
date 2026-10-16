
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

00608470 <.text+0x207470>:
  608470:	8b 85 7c ff ff ff    	mov    eax,DWORD PTR [ebp-0x84]
  608476:	50                   	push   eax
  608477:	68 c0 77 41 00       	push   0x4177c0
  60847c:	ff d6                	call   esi
  60847e:	85 c0                	test   eax,eax
  608480:	75 10                	jne    0x608492
  608482:	e8 69 40 ff ff       	call   0x5fc4f0
  608487:	0f bf c8             	movsx  ecx,ax
  60848a:	89 4d e8             	mov    DWORD PTR [ebp-0x18],ecx
  60848d:	e9 b1 fe ff ff       	jmp    0x608343
