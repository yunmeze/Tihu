
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

00582950 <.text+0x181950>:
  582950:	55                   	push   ebp
  582951:	8b ec                	mov    ebp,esp
  582953:	83 ec 0c             	sub    esp,0xc
  582956:	68 06 32 40 00       	push   0x403206
  58295b:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  582961:	50                   	push   eax
  582962:	64 89 25 00 00 00 00 	mov    DWORD PTR fs:0x0,esp
  582969:	81 ec 98 00 00 00    	sub    esp,0x98
  58296f:	53                   	push   ebx
  582970:	56                   	push   esi
  582971:	57                   	push   edi
  582972:	89 65 f4             	mov    DWORD PTR [ebp-0xc],esp
  582975:	c7 45 f8 f0 1b 40 00 	mov    DWORD PTR [ebp-0x8],0x401bf0
  58297c:	8b 75 08             	mov    esi,DWORD PTR [ebp+0x8]
  58297f:	8b c6                	mov    eax,esi
  582981:	83 e0 01             	and    eax,0x1
  582984:	89 45 fc             	mov    DWORD PTR [ebp-0x4],eax
  582987:	83 e6 fe             	and    esi,0xfffffffe
  58298a:	56                   	push   esi
  58298b:	89 75 08             	mov    DWORD PTR [ebp+0x8],esi
  58298e:	8b 0e                	mov    ecx,DWORD PTR [esi]
  582990:	ff 51 04             	call   DWORD PTR [ecx+0x4]
  582993:	8b 16                	mov    edx,DWORD PTR [esi]
  582995:	33 ff                	xor    edi,edi
  582997:	56                   	push   esi
  582998:	89 7d e8             	mov    DWORD PTR [ebp-0x18],edi
  58299b:	89 7d e4             	mov    DWORD PTR [ebp-0x1c],edi
  58299e:	89 7d e0             	mov    DWORD PTR [ebp-0x20],edi
  5829a1:	89 7d dc             	mov    DWORD PTR [ebp-0x24],edi
  5829a4:	89 7d d8             	mov    DWORD PTR [ebp-0x28],edi
  5829a7:	89 7d c8             	mov    DWORD PTR [ebp-0x38],edi
  5829aa:	89 7d b8             	mov    DWORD PTR [ebp-0x48],edi
  5829ad:	89 7d a8             	mov    DWORD PTR [ebp-0x58],edi
  5829b0:	89 7d 98             	mov    DWORD PTR [ebp-0x68],edi
  5829b3:	89 7d 88             	mov    DWORD PTR [ebp-0x78],edi
  5829b6:	89 7d 84             	mov    DWORD PTR [ebp-0x7c],edi
  5829b9:	ff 92 24 04 00 00    	call   DWORD PTR [edx+0x424]
  5829bf:	50                   	push   eax
  5829c0:	8d 45 e4             	lea    eax,[ebp-0x1c]
  5829c3:	50                   	push   eax
  5829c4:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  5829ca:	8b d8                	mov    ebx,eax
  5829cc:	8d 55 84             	lea    edx,[ebp-0x7c]
  5829cf:	52                   	push   edx
  5829d0:	53                   	push   ebx
  5829d1:	8b 0b                	mov    ecx,DWORD PTR [ebx]
  5829d3:	ff 91 98 00 00 00    	call   DWORD PTR [ecx+0x98]
  5829d9:	3b c7                	cmp    eax,edi
  5829db:	db e2                	fnclex
  5829dd:	7d 12                	jge    0x5829f1
  5829df:	68 98 00 00 00       	push   0x98
  5829e4:	68 b4 d5 40 00       	push   0x40d5b4
  5829e9:	53                   	push   ebx
  5829ea:	50                   	push   eax
  5829eb:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5829f1:	33 db                	xor    ebx,ebx
  5829f3:	66 83 7d 84 ff       	cmp    WORD PTR [ebp-0x7c],0xffff
  5829f8:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  5829fb:	0f 94 c3             	sete   bl
  5829fe:	f7 db                	neg    ebx
  582a00:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  582a06:	66 3b df             	cmp    bx,di
  582a09:	0f 85 e9 01 00 00    	jne    0x582bf8
  582a0f:	8b 06                	mov    eax,DWORD PTR [esi]
  582a11:	56                   	push   esi
  582a12:	ff 90 74 05 00 00    	call   DWORD PTR [eax+0x574]
  582a18:	8d 4d d8             	lea    ecx,[ebp-0x28]
  582a1b:	50                   	push   eax
  582a1c:	51                   	push   ecx
  582a1d:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  582a23:	89 85 68 ff ff ff    	mov    DWORD PTR [ebp-0x98],eax
  582a29:	a1 4c 35 64 00       	mov    eax,ds:0x64354c
  582a2e:	3b c7                	cmp    eax,edi
  582a30:	75 10                	jne    0x582a42
  582a32:	68 4c 35 64 00       	push   0x64354c
  582a37:	68 14 cd 40 00       	push   0x40cd14
  582a3c:	ff 15 c0 11 40 00    	call   DWORD PTR ds:0x4011c0
  582a42:	a1 4c 35 64 00       	mov    eax,ds:0x64354c
  582a47:	8b 35 4c 35 64 00    	mov    esi,DWORD PTR ds:0x64354c
  582a4d:	bb 0a 00 00 00       	mov    ebx,0xa
  582a52:	3b c7                	cmp    eax,edi
  582a54:	c7 45 c0 04 00 02 80 	mov    DWORD PTR [ebp-0x40],0x80020004
  582a5b:	89 5d b8             	mov    DWORD PTR [ebp-0x48],ebx
  582a5e:	75 10                	jne    0x582a70
  582a60:	68 4c 35 64 00       	push   0x64354c
  582a65:	68 14 cd 40 00       	push   0x40cd14
  582a6a:	ff 15 c0 11 40 00    	call   DWORD PTR ds:0x4011c0
  582a70:	a1 4c 35 64 00       	mov    eax,ds:0x64354c
  582a75:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  582a78:	51                   	push   ecx
  582a79:	50                   	push   eax
  582a7a:	8b 10                	mov    edx,DWORD PTR [eax]
  582a7c:	89 45 80             	mov    DWORD PTR [ebp-0x80],eax
  582a7f:	ff 52 14             	call   DWORD PTR [edx+0x14]
  582a82:	3b c7                	cmp    eax,edi
  582a84:	db e2                	fnclex
  582a86:	7d 12                	jge    0x582a9a
  582a88:	8b 55 80             	mov    edx,DWORD PTR [ebp-0x80]
  582a8b:	6a 14                	push   0x14
  582a8d:	68 04 cd 40 00       	push   0x40cd04
  582a92:	52                   	push   edx
  582a93:	50                   	push   eax
  582a94:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582a9a:	8b 45 e4             	mov    eax,DWORD PTR [ebp-0x1c]
  582a9d:	8d 55 e8             	lea    edx,[ebp-0x18]
  582aa0:	52                   	push   edx
  582aa1:	50                   	push   eax
  582aa2:	8b 08                	mov    ecx,DWORD PTR [eax]
  582aa4:	89 85 78 ff ff ff    	mov    DWORD PTR [ebp-0x88],eax
  582aaa:	ff 51 50             	call   DWORD PTR [ecx+0x50]
  582aad:	3b c7                	cmp    eax,edi
  582aaf:	db e2                	fnclex
  582ab1:	7d 15                	jge    0x582ac8
  582ab3:	8b 8d 78 ff ff ff    	mov    ecx,DWORD PTR [ebp-0x88]
  582ab9:	6a 50                	push   0x50
  582abb:	68 24 cd 40 00       	push   0x40cd24
  582ac0:	51                   	push   ecx
  582ac1:	50                   	push   eax
  582ac2:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582ac8:	8b 55 e8             	mov    edx,DWORD PTR [ebp-0x18]
  582acb:	52                   	push   edx
  582acc:	68 d8 fe 40 00       	push   0x40fed8
  582ad1:	ff 15 80 10 40 00    	call   DWORD PTR ds:0x401080
  582ad7:	b9 08 00 00 00       	mov    ecx,0x8
  582adc:	8d 55 e0             	lea    edx,[ebp-0x20]
  582adf:	89 45 d0             	mov    DWORD PTR [ebp-0x30],eax
  582ae2:	89 4d c8             	mov    DWORD PTR [ebp-0x38],ecx
  582ae5:	8b 3e                	mov    edi,DWORD PTR [esi]
  582ae7:	52                   	push   edx
  582ae8:	8b 55 8c             	mov    edx,DWORD PTR [ebp-0x74]
  582aeb:	83 ec 10             	sub    esp,0x10
  582aee:	89 bd 54 ff ff ff    	mov    DWORD PTR [ebp-0xac],edi
  582af4:	8b fc                	mov    edi,esp
  582af6:	83 ec 10             	sub    esp,0x10
  582af9:	89 1f                	mov    DWORD PTR [edi],ebx
  582afb:	89 57 04             	mov    DWORD PTR [edi+0x4],edx
  582afe:	ba 04 00 02 80       	mov    edx,0x80020004
  582b03:	89 57 08             	mov    DWORD PTR [edi+0x8],edx
  582b06:	8b 55 94             	mov    edx,DWORD PTR [ebp-0x6c]
  582b09:	89 57 0c             	mov    DWORD PTR [edi+0xc],edx
  582b0c:	8b fc                	mov    edi,esp
  582b0e:	ba 0a 00 00 00       	mov    edx,0xa
  582b13:	83 ec 10             	sub    esp,0x10
  582b16:	89 17                	mov    DWORD PTR [edi],edx
  582b18:	8b 55 9c             	mov    edx,DWORD PTR [ebp-0x64]
  582b1b:	89 57 04             	mov    DWORD PTR [edi+0x4],edx
  582b1e:	ba 04 00 02 80       	mov    edx,0x80020004
  582b23:	89 57 08             	mov    DWORD PTR [edi+0x8],edx
  582b26:	8b 55 a4             	mov    edx,DWORD PTR [ebp-0x5c]
  582b29:	89 57 0c             	mov    DWORD PTR [edi+0xc],edx
  582b2c:	8b fc                	mov    edi,esp
  582b2e:	ba 0a 00 00 00       	mov    edx,0xa
  582b33:	83 ec 10             	sub    esp,0x10
  582b36:	89 17                	mov    DWORD PTR [edi],edx
  582b38:	8b 55 ac             	mov    edx,DWORD PTR [ebp-0x54]
  582b3b:	89 57 04             	mov    DWORD PTR [edi+0x4],edx
  582b3e:	ba 04 00 02 80       	mov    edx,0x80020004
  582b43:	89 57 08             	mov    DWORD PTR [edi+0x8],edx
  582b46:	8b 55 b4             	mov    edx,DWORD PTR [ebp-0x4c]
  582b49:	89 57 0c             	mov    DWORD PTR [edi+0xc],edx
  582b4c:	8b 7d b8             	mov    edi,DWORD PTR [ebp-0x48]
  582b4f:	8b d4                	mov    edx,esp
  582b51:	83 ec 10             	sub    esp,0x10
  582b54:	89 3a                	mov    DWORD PTR [edx],edi
  582b56:	8b 7d bc             	mov    edi,DWORD PTR [ebp-0x44]
  582b59:	89 7a 04             	mov    DWORD PTR [edx+0x4],edi
  582b5c:	8b 7d c0             	mov    edi,DWORD PTR [ebp-0x40]
  582b5f:	89 7a 08             	mov    DWORD PTR [edx+0x8],edi
  582b62:	8b 7d c4             	mov    edi,DWORD PTR [ebp-0x3c]
  582b65:	89 7a 0c             	mov    DWORD PTR [edx+0xc],edi
  582b68:	8b d4                	mov    edx,esp
  582b6a:	56                   	push   esi
  582b6b:	89 0a                	mov    DWORD PTR [edx],ecx
  582b6d:	8b 4d cc             	mov    ecx,DWORD PTR [ebp-0x34]
  582b70:	89 4a 04             	mov    DWORD PTR [edx+0x4],ecx
  582b73:	8b 8d 54 ff ff ff    	mov    ecx,DWORD PTR [ebp-0xac]
  582b79:	89 42 08             	mov    DWORD PTR [edx+0x8],eax
  582b7c:	8b 45 d4             	mov    eax,DWORD PTR [ebp-0x2c]
  582b7f:	89 42 0c             	mov    DWORD PTR [edx+0xc],eax
  582b82:	ff 51 44             	call   DWORD PTR [ecx+0x44]
  582b85:	33 ff                	xor    edi,edi
  582b87:	3b c7                	cmp    eax,edi
  582b89:	db e2                	fnclex
  582b8b:	7d 0f                	jge    0x582b9c
  582b8d:	6a 44                	push   0x44
  582b8f:	68 04 cd 40 00       	push   0x40cd04
  582b94:	56                   	push   esi
  582b95:	50                   	push   eax
  582b96:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582b9c:	8b 45 e0             	mov    eax,DWORD PTR [ebp-0x20]
  582b9f:	8b b5 68 ff ff ff    	mov    esi,DWORD PTR [ebp-0x98]
  582ba5:	8d 55 dc             	lea    edx,[ebp-0x24]
  582ba8:	50                   	push   eax
  582ba9:	89 7d e0             	mov    DWORD PTR [ebp-0x20],edi
  582bac:	8b 1e                	mov    ebx,DWORD PTR [esi]
  582bae:	52                   	push   edx
  582baf:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  582bb5:	50                   	push   eax
  582bb6:	56                   	push   esi
  582bb7:	ff 53 5c             	call   DWORD PTR [ebx+0x5c]
  582bba:	3b c7                	cmp    eax,edi
  582bbc:	db e2                	fnclex
  582bbe:	7d 0f                	jge    0x582bcf
  582bc0:	6a 5c                	push   0x5c
  582bc2:	68 6c cd 40 00       	push   0x40cd6c
  582bc7:	56                   	push   esi
  582bc8:	50                   	push   eax
  582bc9:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  582bcf:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582bd2:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  582bd8:	8d 45 d8             	lea    eax,[ebp-0x28]
  582bdb:	8d 4d dc             	lea    ecx,[ebp-0x24]
  582bde:	50                   	push   eax
  582bdf:	8d 55 e4             	lea    edx,[ebp-0x1c]
  582be2:	51                   	push   ecx
  582be3:	52                   	push   edx
  582be4:	6a 03                	push   0x3
  582be6:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  582bec:	83 c4 10             	add    esp,0x10
  582bef:	8d 4d c8             	lea    ecx,[ebp-0x38]
  582bf2:	ff 15 40 10 40 00    	call   DWORD PTR ds:0x401040
  582bf8:	89 7d fc             	mov    DWORD PTR [ebp-0x4],edi
  582bfb:	68 31 2c 58 00       	push   0x582c31
  582c00:	eb 2e                	jmp    0x582c30
  582c02:	8d 4d e8             	lea    ecx,[ebp-0x18]
  582c05:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  582c0b:	8d 45 d8             	lea    eax,[ebp-0x28]
  582c0e:	8d 4d dc             	lea    ecx,[ebp-0x24]
  582c11:	50                   	push   eax
  582c12:	8d 55 e0             	lea    edx,[ebp-0x20]
  582c15:	51                   	push   ecx
  582c16:	8d 45 e4             	lea    eax,[ebp-0x1c]
  582c19:	52                   	push   edx
  582c1a:	50                   	push   eax
  582c1b:	6a 04                	push   0x4
  582c1d:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  582c23:	83 c4 14             	add    esp,0x14
  582c26:	8d 4d c8             	lea    ecx,[ebp-0x38]
  582c29:	ff 15 40 10 40 00    	call   DWORD PTR ds:0x401040
  582c2f:	c3                   	ret
  582c30:	c3                   	ret
  582c31:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  582c34:	50                   	push   eax
  582c35:	8b 08                	mov    ecx,DWORD PTR [eax]
  582c37:	ff 51 08             	call   DWORD PTR [ecx+0x8]
  582c3a:	8b 45 fc             	mov    eax,DWORD PTR [ebp-0x4]
  582c3d:	8b 4d ec             	mov    ecx,DWORD PTR [ebp-0x14]
  582c40:	5f                   	pop    edi
  582c41:	5e                   	pop    esi
  582c42:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  582c49:	5b                   	pop    ebx
  582c4a:	8b e5                	mov    esp,ebp
  582c4c:	5d                   	pop    ebp
  582c4d:	c2 14 00             	ret    0x14
