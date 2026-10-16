
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

005ee580 <.text+0x1ed580>:
  5ee580:	c8 63 00 2b          	enter  0x63,0x2b
  5ee584:	42                   	inc    edx
  5ee585:	14 8b                	adc    al,0x8b
  5ee587:	c8 c1 e1 05          	enter  0xe1c1,0x5
  5ee58b:	2b c8                	sub    ecx,eax
  5ee58d:	8d 0c c9             	lea    ecx,[ecx+ecx*8]
  5ee590:	8d 0c 48             	lea    ecx,[eax+ecx*2]
  5ee593:	8d 04 88             	lea    eax,[eax+ecx*4]
  5ee596:	8b 4a 0c             	mov    ecx,DWORD PTR [edx+0xc]
  5ee599:	8b 94 81 e0 1f 00 00 	mov    edx,DWORD PTR [ecx+eax*4+0x1fe0]
  5ee5a0:	52                   	push   edx
  5ee5a1:	ff 15 34 10 40 00    	call   DWORD PTR ds:0x401034
  5ee5a7:	8b d0                	mov    edx,eax
  5ee5a9:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee5ac:	ff 15 3c 12 40 00    	call   DWORD PTR ds:0x40123c
  5ee5b2:	89 9d 48 ff ff ff    	mov    DWORD PTR [ebp-0xb8],ebx
  5ee5b8:	8b 9d 74 ff ff ff    	mov    ebx,DWORD PTR [ebp-0x8c]
  5ee5be:	50                   	push   eax
  5ee5bf:	8b 85 48 ff ff ff    	mov    eax,DWORD PTR [ebp-0xb8]
  5ee5c5:	53                   	push   ebx
  5ee5c6:	ff 50 54             	call   DWORD PTR [eax+0x54]
  5ee5c9:	85 c0                	test   eax,eax
  5ee5cb:	db e2                	fnclex
  5ee5cd:	7d 0f                	jge    0x5ee5de
  5ee5cf:	6a 54                	push   0x54
  5ee5d1:	68 0c d6 40 00       	push   0x40d60c
  5ee5d6:	53                   	push   ebx
  5ee5d7:	50                   	push   eax
  5ee5d8:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5ee5de:	8b 1d 80 12 40 00    	mov    ebx,DWORD PTR ds:0x401280
  5ee5e4:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee5e7:	ff d3                	call   ebx
  5ee5e9:	8d 4d dc             	lea    ecx,[ebp-0x24]
  5ee5ec:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  5ee5f2:	ba 54 59 41 00       	mov    edx,0x415954
  5ee5f7:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee5fa:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  5ee600:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee603:	51                   	push   ecx
  5ee604:	e8 b7 84 04 00       	call   0x636ac0
  5ee609:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee60c:	ff d3                	call   ebx
  5ee60e:	8b 5d ec             	mov    ebx,DWORD PTR [ebp-0x14]
  5ee611:	e9 6c 02 00 00       	jmp    0x5ee882
  5ee616:	e8 d5 de 00 00       	call   0x5fc4f0
  5ee61b:	66 85 c0             	test   ax,ax
  5ee61e:	75 55                	jne    0x5ee675
  5ee620:	68 ff 00 00 00       	push   0xff
  5ee625:	53                   	push   ebx
  5ee626:	6a 32                	push   0x32
  5ee628:	68 ff 00 00 00       	push   0xff
  5ee62d:	ff 15 14 10 40 00    	call   DWORD PTR ds:0x401014
  5ee633:	ba 64 59 41 00       	mov    edx,0x415964
  5ee638:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee63b:	c7 85 7c ff ff ff 00 	mov    DWORD PTR [ebp-0x84],0x33000000
  5ee642:	00 00 33 
  5ee645:	89 45 80             	mov    DWORD PTR [ebp-0x80],eax
  5ee648:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  5ee64e:	8d 95 7c ff ff ff    	lea    edx,[ebp-0x84]
  5ee654:	8d 45 80             	lea    eax,[ebp-0x80]
  5ee657:	52                   	push   edx
  5ee658:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee65b:	50                   	push   eax
  5ee65c:	51                   	push   ecx
  5ee65d:	e8 2e 8f fb ff       	call   0x5a7590
  5ee662:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee665:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  5ee66b:	68 97 ef 5e 00       	push   0x5eef97
  5ee670:	e9 18 09 00 00       	jmp    0x5eef8d
  5ee675:	e8 76 df 00 00       	call   0x5fc5f0
  5ee67a:	0f bf 16             	movsx  edx,WORD PTR [esi]
  5ee67d:	8b 0d 88 ed 63 00    	mov    ecx,DWORD PTR ds:0x63ed88
  5ee683:	2b 51 14             	sub    edx,DWORD PTR [ecx+0x14]
  5ee686:	0f af 51 18          	imul   edx,DWORD PTR [ecx+0x18]
  5ee68a:	2b 51 1c             	sub    edx,DWORD PTR [ecx+0x1c]
  5ee68d:	0f bf 0f             	movsx  ecx,WORD PTR [edi]
  5ee690:	03 d1                	add    edx,ecx
  5ee692:	8b 0d 88 ed 63 00    	mov    ecx,DWORD PTR ds:0x63ed88
  5ee698:	8b 49 0c             	mov    ecx,DWORD PTR [ecx+0xc]
  5ee69b:	0f bf 0c 51          	movsx  ecx,WORD PTR [ecx+edx*2]
  5ee69f:	8b 15 84 ed 63 00    	mov    edx,DWORD PTR ds:0x63ed84
  5ee6a5:	2b 4a 14             	sub    ecx,DWORD PTR [edx+0x14]
  5ee6a8:	8d 14 cd 00 00 00 00 	lea    edx,[ecx*8+0x0]
  5ee6af:	2b d1                	sub    edx,ecx
  5ee6b1:	8d 0c 92             	lea    ecx,[edx+edx*4]
  5ee6b4:	8b 15 84 ed 63 00    	mov    edx,DWORD PTR ds:0x63ed84
  5ee6ba:	8b 52 0c             	mov    edx,DWORD PTR [edx+0xc]
  5ee6bd:	66 39 84 8a 80 00 00 	cmp    WORD PTR [edx+ecx*4+0x80],ax
  5ee6c4:	00 
  5ee6c5:	7e 55                	jle    0x5ee71c
  5ee6c7:	68 ff 00 00 00       	push   0xff
  5ee6cc:	53                   	push   ebx
  5ee6cd:	6a 32                	push   0x32
  5ee6cf:	68 ff 00 00 00       	push   0xff
  5ee6d4:	ff 15 14 10 40 00    	call   DWORD PTR ds:0x401014
  5ee6da:	ba 80 59 41 00       	mov    edx,0x415980
  5ee6df:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee6e2:	c7 85 7c ff ff ff 00 	mov    DWORD PTR [ebp-0x84],0x33000000
  5ee6e9:	00 00 33 
  5ee6ec:	89 45 80             	mov    DWORD PTR [ebp-0x80],eax
  5ee6ef:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  5ee6f5:	8d 85 7c ff ff ff    	lea    eax,[ebp-0x84]
  5ee6fb:	8d 4d 80             	lea    ecx,[ebp-0x80]
  5ee6fe:	50                   	push   eax
  5ee6ff:	8d 55 e0             	lea    edx,[ebp-0x20]
  5ee702:	51                   	push   ecx
  5ee703:	52                   	push   edx
  5ee704:	e8 87 8e fb ff       	call   0x5a7590
  5ee709:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee70c:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  5ee712:	68 97 ef 5e 00       	push   0x5eef97
  5ee717:	e9 71 08 00 00       	jmp    0x5eef8d
  5ee71c:	a1 84 ed 63 00       	mov    eax,ds:0x63ed84
  5ee721:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  5ee724:	50                   	push   eax
  5ee725:	51                   	push   ecx
  5ee726:	ff 15 10 12 40 00    	call   DWORD PTR ds:0x401210
  5ee72c:	a1 88 ed 63 00       	mov    eax,ds:0x63ed88
  5ee731:	0f bf 16             	movsx  edx,WORD PTR [esi]
  5ee734:	8b 48 14             	mov    ecx,DWORD PTR [eax+0x14]
  5ee737:	2b d1                	sub    edx,ecx
  5ee739:	8b 48 1c             	mov    ecx,DWORD PTR [eax+0x1c]
  5ee73c:	0f af 50 18          	imul   edx,DWORD PTR [eax+0x18]
  5ee740:	8b 40 0c             	mov    eax,DWORD PTR [eax+0xc]
  5ee743:	2b d1                	sub    edx,ecx
  5ee745:	0f bf 0f             	movsx  ecx,WORD PTR [edi]
  5ee748:	03 d1                	add    edx,ecx
  5ee74a:	0f bf 04 50          	movsx  eax,WORD PTR [eax+edx*2]
  5ee74e:	8b 55 e4             	mov    edx,DWORD PTR [ebp-0x1c]
  5ee751:	8b 4a 14             	mov    ecx,DWORD PTR [edx+0x14]
  5ee754:	8b 52 0c             	mov    edx,DWORD PTR [edx+0xc]
  5ee757:	2b c1                	sub    eax,ecx
  5ee759:	8d 0c c5 00 00 00 00 	lea    ecx,[eax*8+0x0]
  5ee760:	2b c8                	sub    ecx,eax
  5ee762:	8d 0c 89             	lea    ecx,[ecx+ecx*4]
  5ee765:	8d 44 8a 04          	lea    eax,[edx+ecx*4+0x4]
  5ee769:	50                   	push   eax
  5ee76a:	e8 11 de 00 00       	call   0x5fc580
  5ee76f:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  5ee772:	89 45 84             	mov    DWORD PTR [ebp-0x7c],eax
  5ee775:	51                   	push   ecx
  5ee776:	ff 15 70 12 40 00    	call   DWORD PTR ds:0x401270
  5ee77c:	66 83 7d 84 ff       	cmp    WORD PTR [ebp-0x7c],0xffff
  5ee781:	75 31                	jne    0x5ee7b4
  5ee783:	ba 9c 59 41 00       	mov    edx,0x41599c
  5ee788:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee78b:	89 5d 84             	mov    DWORD PTR [ebp-0x7c],ebx
  5ee78e:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  5ee794:	8d 55 84             	lea    edx,[ebp-0x7c]
  5ee797:	8d 45 e0             	lea    eax,[ebp-0x20]
  5ee79a:	52                   	push   edx
  5ee79b:	50                   	push   eax
  5ee79c:	e8 ff 4e 00 00       	call   0x5f36a0
  5ee7a1:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5ee7a4:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  5ee7aa:	68 97 ef 5e 00       	push   0x5eef97
  5ee7af:	e9 d9 07 00 00       	jmp    0x5eef8d
  5ee7b4:	e8 a7 de 00 00       	call   0x5fc660
  5ee7b9:	0f bf 0e             	movsx  ecx,WORD PTR [esi]
  5ee7bc:	8b d8                	mov    ebx,eax
  5ee7be:	a1 88 ed 63 00       	mov    eax,ds:0x63ed88
  5ee7c3:	8b 50 14             	mov    edx,DWORD PTR [eax+0x14]
  5ee7c6:	2b ca                	sub    ecx,edx
  5ee7c8:	8b 50 1c             	mov    edx,DWORD PTR [eax+0x1c]
  5ee7cb:	0f af 48 18          	imul   ecx,DWORD PTR [eax+0x18]
  5ee7cf:	8b 40 0c             	mov    eax,DWORD PTR [eax+0xc]
  5ee7d2:	2b ca                	sub    ecx,edx
  5ee7d4:	0f bf 17             	movsx  edx,WORD PTR [edi]
  5ee7d7:	03 ca                	add    ecx,edx
  5ee7d9:	8b 15 84 ed 63 00    	mov    edx,DWORD PTR ds:0x63ed84
  5ee7df:	0f bf 04 48          	movsx  eax,WORD PTR [eax+ecx*2]
  5ee7e3:	8b 4a 14             	mov    ecx,DWORD PTR [edx+0x14]
  5ee7e6:	8b 52 0c             	mov    edx,DWORD PTR [edx+0xc]
  5ee7e9:	2b c1                	sub    eax,ecx
  5ee7eb:	8d 0c c5 00 00 00 00 	lea    ecx,[eax*8+0x0]
  5ee7f2:	2b c8                	sub    ecx,eax
  5ee7f4:	8d 0c 89             	lea    ecx,[ecx+ecx*4]
  5ee7f7:	8d 04 8a             	lea    eax,[edx+ecx*4]
  5ee7fa:	8b 15 bc a0 63 00    	mov    edx,DWORD PTR ds:0x63a0bc
  5ee800:	0f bf cb             	movsx  ecx,bx
  5ee803:	50                   	push   eax
  5ee804:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  5ee80b:	2b c1                	sub    eax,ecx
  5ee80d:	8d 0c 80             	lea    ecx,[eax+eax*4]
  5ee810:	8d 04 8a             	lea    eax,[edx+ecx*4]
  5ee813:	50                   	push   eax
  5ee814:	68 d0 bb 40 00       	push   0x40bbd0
  5ee819:	ff 15 88 12 40 00    	call   DWORD PTR ds:0x401288
  5ee81f:	e8 4c 86 fe ff       	call   0x5d6e70
  5ee824:	8b 0d 84 ed 63 00    	mov    ecx,DWORD PTR ds:0x63ed84
  5ee82a:	8d 55 e4             	lea    edx,[ebp-0x1c]
  5ee82d:	51                   	push   ecx
  5ee82e:	52                   	push   edx
  5ee82f:	ff 15 10 12 40 00    	call   DWORD PTR ds:0x401210
  5ee835:	a1 88 ed 63 00       	mov    eax,ds:0x63ed88
  5ee83a:	0f bf 0e             	movsx  ecx,WORD PTR [esi]
  5ee83d:	8b 50 14             	mov    edx,DWORD PTR [eax+0x14]
  5ee840:	2b ca                	sub    ecx,edx
  5ee842:	8b 50 1c             	mov    edx,DWORD PTR [eax+0x1c]
  5ee845:	0f af 48 18          	imul   ecx,DWORD PTR [eax+0x18]
  5ee849:	8b 40 0c             	mov    eax,DWORD PTR [eax+0xc]
  5ee84c:	2b ca                	sub    ecx,edx
  5ee84e:	0f                   	.byte 0xf
  5ee84f:	bf                   	.byte 0xbf
