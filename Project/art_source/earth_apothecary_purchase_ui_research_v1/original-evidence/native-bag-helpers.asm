
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

005fc4f0 <.text+0x1fb4f0>:
  5fc4f0:	53                   	push   ebx
  5fc4f1:	8b 1d 4c 10 40 00    	mov    ebx,DWORD PTR ds:0x40104c
  5fc4f7:	55                   	push   ebp
  5fc4f8:	56                   	push   esi
  5fc4f9:	57                   	push   edi
  5fc4fa:	33 ed                	xor    ebp,ebp
  5fc4fc:	be 34 08 00 00       	mov    esi,0x834
  5fc501:	bf 2a 00 00 00       	mov    edi,0x2a
  5fc506:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  5fc50b:	8b 4c 06 2c          	mov    ecx,DWORD PTR [esi+eax*1+0x2c]
  5fc50f:	51                   	push   ecx
  5fc510:	ff d3                	call   ebx
  5fc512:	83 f8 01             	cmp    eax,0x1
  5fc515:	7e 01                	jle    0x5fc518
  5fc517:	45                   	inc    ebp
  5fc518:	81 c6 8c 00 00 00    	add    esi,0x8c
  5fc51e:	4f                   	dec    edi
  5fc51f:	75 e5                	jne    0x5fc506
  5fc521:	b8 2a 00 00 00       	mov    eax,0x2a
  5fc526:	5f                   	pop    edi
  5fc527:	2b c5                	sub    eax,ebp
  5fc529:	5e                   	pop    esi
  5fc52a:	5d                   	pop    ebp
  5fc52b:	5b                   	pop    ebx
  5fc52c:	c3                   	ret
  5fc52d:	90                   	nop
  5fc52e:	90                   	nop
  5fc52f:	90                   	nop
  5fc530:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  5fc535:	53                   	push   ebx
  5fc536:	8b 1d 4c 10 40 00    	mov    ebx,DWORD PTR ds:0x40104c
  5fc53c:	55                   	push   ebp
  5fc53d:	56                   	push   esi
  5fc53e:	57                   	push   edi
  5fc53f:	33 ff                	xor    edi,edi
  5fc541:	33 f6                	xor    esi,esi
  5fc543:	bd 39 00 00 00       	mov    ebp,0x39
  5fc548:	8b 44 06 2c          	mov    eax,DWORD PTR [esi+eax*1+0x2c]
  5fc54c:	50                   	push   eax
  5fc54d:	ff d3                	call   ebx
  5fc54f:	83 f8 01             	cmp    eax,0x1
  5fc552:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  5fc557:	7e 0a                	jle    0x5fc563
  5fc559:	66 8b 8c 06 80 00 00 	mov    cx,WORD PTR [esi+eax*1+0x80]
  5fc560:	00 
  5fc561:	03 f9                	add    edi,ecx
  5fc563:	81 c6 8c 00 00 00    	add    esi,0x8c
  5fc569:	4d                   	dec    ebp
  5fc56a:	75 dc                	jne    0x5fc548
  5fc56c:	66 8b c7             	mov    ax,di
  5fc56f:	5f                   	pop    edi
  5fc570:	5e                   	pop    esi
  5fc571:	5d                   	pop    ebp
  5fc572:	5b                   	pop    ebx
  5fc573:	c3                   	ret
  5fc574:	90                   	nop
  5fc575:	90                   	nop
  5fc576:	90                   	nop
  5fc577:	90                   	nop
  5fc578:	90                   	nop
  5fc579:	90                   	nop
  5fc57a:	90                   	nop
  5fc57b:	90                   	nop
  5fc57c:	90                   	nop
  5fc57d:	90                   	nop
  5fc57e:	90                   	nop
  5fc57f:	90                   	nop
  5fc580:	53                   	push   ebx
  5fc581:	8b 1d 4c 10 40 00    	mov    ebx,DWORD PTR ds:0x40104c
  5fc587:	55                   	push   ebp
  5fc588:	8b 6c 24 0c          	mov    ebp,DWORD PTR [esp+0xc]
  5fc58c:	56                   	push   esi
  5fc58d:	57                   	push   edi
  5fc58e:	33 ff                	xor    edi,edi
  5fc590:	0f bf cf             	movsx  ecx,di
  5fc593:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  5fc59a:	2b c1                	sub    eax,ecx
  5fc59c:	8d 34 80             	lea    esi,[eax+eax*4]
  5fc59f:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  5fc5a4:	c1 e6 02             	shl    esi,0x2
  5fc5a7:	8b 4c 06 2c          	mov    ecx,DWORD PTR [esi+eax*1+0x2c]
  5fc5ab:	51                   	push   ecx
  5fc5ac:	ff d3                	call   ebx
  5fc5ae:	83 f8 01             	cmp    eax,0x1
  5fc5b1:	7e 19                	jle    0x5fc5cc
  5fc5b3:	8b 15 bc a0 63 00    	mov    edx,DWORD PTR ds:0x63a0bc
  5fc5b9:	8b 4d 00             	mov    ecx,DWORD PTR [ebp+0x0]
  5fc5bc:	8b 44 16 04          	mov    eax,DWORD PTR [esi+edx*1+0x4]
  5fc5c0:	50                   	push   eax
  5fc5c1:	51                   	push   ecx
  5fc5c2:	ff 15 0c 11 40 00    	call   DWORD PTR ds:0x40110c
  5fc5c8:	85 c0                	test   eax,eax
  5fc5ca:	74 11                	je     0x5fc5dd
  5fc5cc:	47                   	inc    edi
  5fc5cd:	66 81 ff 78 02       	cmp    di,0x278
  5fc5d2:	7e bc                	jle    0x5fc590
  5fc5d4:	5f                   	pop    edi
  5fc5d5:	5e                   	pop    esi
  5fc5d6:	5d                   	pop    ebp
  5fc5d7:	33 c0                	xor    eax,eax
  5fc5d9:	5b                   	pop    ebx
  5fc5da:	c2 04 00             	ret    0x4
  5fc5dd:	5f                   	pop    edi
  5fc5de:	5e                   	pop    esi
  5fc5df:	5d                   	pop    ebp
  5fc5e0:	83 c8 ff             	or     eax,0xffffffff
  5fc5e3:	5b                   	pop    ebx
  5fc5e4:	c2 04 00             	ret    0x4
  5fc5e7:	90                   	nop
  5fc5e8:	90                   	nop
  5fc5e9:	90                   	nop
  5fc5ea:	90                   	nop
  5fc5eb:	90                   	nop
  5fc5ec:	90                   	nop
  5fc5ed:	90                   	nop
  5fc5ee:	90                   	nop
  5fc5ef:	90                   	nop
  5fc5f0:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  5fc5f5:	53                   	push   ebx
  5fc5f6:	8b 1d 4c 10 40 00    	mov    ebx,DWORD PTR ds:0x40104c
  5fc5fc:	55                   	push   ebp
  5fc5fd:	56                   	push   esi
  5fc5fe:	57                   	push   edi
  5fc5ff:	33 ff                	xor    edi,edi
  5fc601:	33 f6                	xor    esi,esi
  5fc603:	bd 39 00 00 00       	mov    ebp,0x39
  5fc608:	8b 44 06 2c          	mov    eax,DWORD PTR [esi+eax*1+0x2c]
  5fc60c:	50                   	push   eax
  5fc60d:	ff d3                	call   ebx
  5fc60f:	83 f8 01             	cmp    eax,0x1
  5fc612:	a1 bc a0 63 00       	mov    eax,ds:0x63a0bc
  5fc617:	7e 0a                	jle    0x5fc623
  5fc619:	66 8b 8c 06 80 00 00 	mov    cx,WORD PTR [esi+eax*1+0x80]
  5fc620:	00 
  5fc621:	03 f9                	add    edi,ecx
  5fc623:	81 c6 8c 00 00 00    	add    esi,0x8c
  5fc629:	4d                   	dec    ebp
  5fc62a:	75 dc                	jne    0x5fc608
  5fc62c:	8b 15 ac c8 63 00    	mov    edx,DWORD PTR ds:0x63c8ac
  5fc632:	0f bf 05 a4 c8 63 00 	movsx  eax,WORD PTR ds:0x63c8a4
  5fc639:	2b 42 14             	sub    eax,DWORD PTR [edx+0x14]
  5fc63c:	8b c8                	mov    ecx,eax
  5fc63e:	c1 e1 05             	shl    ecx,0x5
  5fc641:	2b c8                	sub    ecx,eax
  5fc643:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  5fc646:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  5fc649:	8d 04 88             	lea    eax,[eax+ecx*4]
  5fc64c:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  5fc64f:	66 8b 84 81 80 20 00 	mov    ax,WORD PTR [ecx+eax*4+0x2080]
  5fc656:	00 
  5fc657:	66 2b c7             	sub    ax,di
  5fc65a:	5f                   	pop    edi
  5fc65b:	5e                   	pop    esi
  5fc65c:	5d                   	pop    ebp
  5fc65d:	5b                   	pop    ebx
  5fc65e:	c3                   	ret
  5fc65f:	90                   	nop
  5fc660:	53                   	push   ebx
  5fc661:	56                   	push   esi
  5fc662:	57                   	push   edi
  5fc663:	8b 3d 4c 10 40 00    	mov    edi,DWORD PTR ds:0x40104c
  5fc669:	83 cb ff             	or     ebx,0xffffffff
  5fc66c:	be 0f 00 00 00       	mov    esi,0xf
  5fc671:	0f bf ce             	movsx  ecx,si
  5fc674:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  5fc67b:	2b c1                	sub    eax,ecx
  5fc67d:	8b 0d bc a0 63 00    	mov    ecx,DWORD PTR ds:0x63a0bc
  5fc683:	8d 04 80             	lea    eax,[eax+eax*4]
  5fc686:	8b 54 81 2c          	mov    edx,DWORD PTR [ecx+eax*4+0x2c]
  5fc68a:	52                   	push   edx
  5fc68b:	ff d7                	call   edi
  5fc68d:	83 f8 01             	cmp    eax,0x1
  5fc690:	7e 0e                	jle    0x5fc6a0
  5fc692:	46                   	inc    esi
  5fc693:	66 83 fe 38          	cmp    si,0x38
  5fc697:	7e d8                	jle    0x5fc671
  5fc699:	5f                   	pop    edi
  5fc69a:	66 8b c3             	mov    ax,bx
  5fc69d:	5e                   	pop    esi
  5fc69e:	5b                   	pop    ebx
  5fc69f:	c3                   	ret
  5fc6a0:	66 8b c6             	mov    ax,si
  5fc6a3:	5f                   	pop    edi
  5fc6a4:	5e                   	pop    esi
  5fc6a5:	5b                   	pop    ebx
  5fc6a6:	c3                   	ret
  5fc6a7:	90                   	nop
  5fc6a8:	90                   	nop
  5fc6a9:	90                   	nop
  5fc6aa:	90                   	nop
  5fc6ab:	90                   	nop
  5fc6ac:	90                   	nop
  5fc6ad:	90                   	nop
  5fc6ae:	90                   	nop
  5fc6af:	90                   	nop
