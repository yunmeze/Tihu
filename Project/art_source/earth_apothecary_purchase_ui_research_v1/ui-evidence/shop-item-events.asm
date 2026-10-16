
/workspace/scratch/22c897619190/tihu-legend/原版游戏/LP传奇单机版_重生.exe:     file format pei-i386


Disassembly of section .text:

00583000 <.text+0x182000>:
  583000:	55                   	push   ebp
  583001:	8b ec                	mov    ebp,esp
  583003:	83 ec 0c             	sub    esp,0xc
  583006:	68 06 32 40 00       	push   0x403206
  58300b:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  583011:	50                   	push   eax
  583012:	64 89 25 00 00 00 00 	mov    DWORD PTR fs:0x0,esp
  583019:	83 ec 38             	sub    esp,0x38
  58301c:	53                   	push   ebx
  58301d:	56                   	push   esi
  58301e:	57                   	push   edi
  58301f:	89 65 f4             	mov    DWORD PTR [ebp-0xc],esp
  583022:	c7 45 f8 10 1c 40 00 	mov    DWORD PTR [ebp-0x8],0x401c10
  583029:	8b 75 08             	mov    esi,DWORD PTR [ebp+0x8]
  58302c:	8b c6                	mov    eax,esi
  58302e:	83 e0 01             	and    eax,0x1
  583031:	89 45 fc             	mov    DWORD PTR [ebp-0x4],eax
  583034:	83 e6 fe             	and    esi,0xfffffffe
  583037:	56                   	push   esi
  583038:	89 75 08             	mov    DWORD PTR [ebp+0x8],esi
  58303b:	8b 0e                	mov    ecx,DWORD PTR [esi]
  58303d:	ff 51 04             	call   DWORD PTR [ecx+0x4]
  583040:	8b 16                	mov    edx,DWORD PTR [esi]
  583042:	33 c0                	xor    eax,eax
  583044:	56                   	push   esi
  583045:	89 45 e8             	mov    DWORD PTR [ebp-0x18],eax
  583048:	89 45 e4             	mov    DWORD PTR [ebp-0x1c],eax
  58304b:	89 45 e0             	mov    DWORD PTR [ebp-0x20],eax
  58304e:	89 45 dc             	mov    DWORD PTR [ebp-0x24],eax
  583051:	89 45 d8             	mov    DWORD PTR [ebp-0x28],eax
  583054:	89 45 d4             	mov    DWORD PTR [ebp-0x2c],eax
  583057:	ff 92 24 04 00 00    	call   DWORD PTR [edx+0x424]
  58305d:	8b 1d bc 10 40 00    	mov    ebx,DWORD PTR ds:0x4010bc
  583063:	50                   	push   eax
  583064:	8d 45 e4             	lea    eax,[ebp-0x1c]
  583067:	50                   	push   eax
  583068:	ff d3                	call   ebx
  58306a:	8b f8                	mov    edi,eax
  58306c:	8d 55 d8             	lea    edx,[ebp-0x28]
  58306f:	52                   	push   edx
  583070:	57                   	push   edi
  583071:	8b 0f                	mov    ecx,DWORD PTR [edi]
  583073:	ff 91 98 00 00 00    	call   DWORD PTR [ecx+0x98]
  583079:	85 c0                	test   eax,eax
  58307b:	db e2                	fnclex
  58307d:	7d 12                	jge    0x583091
  58307f:	68 98 00 00 00       	push   0x98
  583084:	68 b4 d5 40 00       	push   0x40d5b4
  583089:	57                   	push   edi
  58308a:	50                   	push   eax
  58308b:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583091:	33 c0                	xor    eax,eax
  583093:	66 83 7d d8 ff       	cmp    WORD PTR [ebp-0x28],0xffff
  583098:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  58309b:	0f 94 c0             	sete   al
  58309e:	f7 d8                	neg    eax
  5830a0:	66 8b f8             	mov    di,ax
  5830a3:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  5830a9:	66 85 ff             	test   di,di
  5830ac:	0f 85 aa 02 00 00    	jne    0x58335c
  5830b2:	8b 4d 10             	mov    ecx,DWORD PTR [ebp+0x10]
  5830b5:	66 83 39 01          	cmp    WORD PTR [ecx],0x1
  5830b9:	0f 85 7d 02 00 00    	jne    0x58333c
  5830bf:	8b 55 0c             	mov    edx,DWORD PTR [ebp+0xc]
  5830c2:	0f bf 0a             	movsx  ecx,WORD PTR [edx]
  5830c5:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  5830cc:	2b c1                	sub    eax,ecx
  5830ce:	8b 0d c0 ed 63 00    	mov    ecx,DWORD PTR ds:0x63edc0
  5830d4:	8d 04 80             	lea    eax,[eax+eax*4]
  5830d7:	8b 54 81 2c          	mov    edx,DWORD PTR [ecx+eax*4+0x2c]
  5830db:	52                   	push   edx
  5830dc:	ff 15 4c 10 40 00    	call   DWORD PTR ds:0x40104c
  5830e2:	83 f8 01             	cmp    eax,0x1
  5830e5:	0f 8e 0a 02 00 00    	jle    0x5832f5
  5830eb:	8b 06                	mov    eax,DWORD PTR [esi]
  5830ed:	56                   	push   esi
  5830ee:	ff 90 7c 05 00 00    	call   DWORD PTR [eax+0x57c]
  5830f4:	8d 4d dc             	lea    ecx,[ebp-0x24]
  5830f7:	50                   	push   eax
  5830f8:	51                   	push   ecx
  5830f9:	ff d3                	call   ebx
  5830fb:	8b 16                	mov    edx,DWORD PTR [esi]
  5830fd:	56                   	push   esi
  5830fe:	89 45 c0             	mov    DWORD PTR [ebp-0x40],eax
  583101:	ff 92 78 05 00 00    	call   DWORD PTR [edx+0x578]
  583107:	50                   	push   eax
  583108:	8d 45 e4             	lea    eax,[ebp-0x1c]
  58310b:	50                   	push   eax
  58310c:	ff d3                	call   ebx
  58310e:	8b f8                	mov    edi,eax
  583110:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]
  583113:	8d 55 e0             	lea    edx,[ebp-0x20]
  583116:	8b 0f                	mov    ecx,DWORD PTR [edi]
  583118:	52                   	push   edx
  583119:	66 8b 10             	mov    dx,WORD PTR [eax]
  58311c:	52                   	push   edx
  58311d:	57                   	push   edi
  58311e:	ff 51 40             	call   DWORD PTR [ecx+0x40]
  583121:	85 c0                	test   eax,eax
  583123:	db e2                	fnclex
  583125:	7d 0f                	jge    0x583136
  583127:	6a 40                	push   0x40
  583129:	68 c4 d5 40 00       	push   0x40d5c4
  58312e:	57                   	push   edi
  58312f:	50                   	push   eax
  583130:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583136:	8b 45 e0             	mov    eax,DWORD PTR [ebp-0x20]
  583139:	8d 55 d4             	lea    edx,[ebp-0x2c]
  58313c:	52                   	push   edx
  58313d:	50                   	push   eax
  58313e:	8b 08                	mov    ecx,DWORD PTR [eax]
  583140:	8b f8                	mov    edi,eax
  583142:	ff 51 60             	call   DWORD PTR [ecx+0x60]
  583145:	85 c0                	test   eax,eax
  583147:	db e2                	fnclex
  583149:	7d 0f                	jge    0x58315a
  58314b:	6a 60                	push   0x60
  58314d:	68 6c cd 40 00       	push   0x40cd6c
  583152:	57                   	push   edi
  583153:	50                   	push   eax
  583154:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  58315a:	8b 7d c0             	mov    edi,DWORD PTR [ebp-0x40]
  58315d:	8b 4d d4             	mov    ecx,DWORD PTR [ebp-0x2c]
  583160:	51                   	push   ecx
  583161:	57                   	push   edi
  583162:	8b 07                	mov    eax,DWORD PTR [edi]
  583164:	ff 50 6c             	call   DWORD PTR [eax+0x6c]
  583167:	85 c0                	test   eax,eax
  583169:	db e2                	fnclex
  58316b:	7d 0f                	jge    0x58317c
  58316d:	6a 6c                	push   0x6c
  58316f:	68 fc d5 40 00       	push   0x40d5fc
  583174:	57                   	push   edi
  583175:	50                   	push   eax
  583176:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  58317c:	8d 55 dc             	lea    edx,[ebp-0x24]
  58317f:	8d 45 e0             	lea    eax,[ebp-0x20]
  583182:	52                   	push   edx
  583183:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  583186:	50                   	push   eax
  583187:	51                   	push   ecx
  583188:	6a 03                	push   0x3
  58318a:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  583190:	8b 16                	mov    edx,DWORD PTR [esi]
  583192:	83 c4 10             	add    esp,0x10
  583195:	56                   	push   esi
  583196:	ff 92 7c 05 00 00    	call   DWORD PTR [edx+0x57c]
  58319c:	50                   	push   eax
  58319d:	8d 45 dc             	lea    eax,[ebp-0x24]
  5831a0:	50                   	push   eax
  5831a1:	ff d3                	call   ebx
  5831a3:	8b 0e                	mov    ecx,DWORD PTR [esi]
  5831a5:	56                   	push   esi
  5831a6:	89 45 c0             	mov    DWORD PTR [ebp-0x40],eax
  5831a9:	ff 91 78 05 00 00    	call   DWORD PTR [ecx+0x578]
  5831af:	8d 55 e4             	lea    edx,[ebp-0x1c]
  5831b2:	50                   	push   eax
  5831b3:	52                   	push   edx
  5831b4:	ff d3                	call   ebx
  5831b6:	8b 55 0c             	mov    edx,DWORD PTR [ebp+0xc]
  5831b9:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5831bc:	8b f8                	mov    edi,eax
  5831be:	51                   	push   ecx
  5831bf:	66 8b 0a             	mov    cx,WORD PTR [edx]
  5831c2:	8b 07                	mov    eax,DWORD PTR [edi]
  5831c4:	51                   	push   ecx
  5831c5:	57                   	push   edi
  5831c6:	ff 50 40             	call   DWORD PTR [eax+0x40]
  5831c9:	85 c0                	test   eax,eax
  5831cb:	db e2                	fnclex
  5831cd:	7d 0f                	jge    0x5831de
  5831cf:	6a 40                	push   0x40
  5831d1:	68 c4 d5 40 00       	push   0x40d5c4
  5831d6:	57                   	push   edi
  5831d7:	50                   	push   eax
  5831d8:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5831de:	8b 45 e0             	mov    eax,DWORD PTR [ebp-0x20]
  5831e1:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  5831e4:	51                   	push   ecx
  5831e5:	50                   	push   eax
  5831e6:	8b 10                	mov    edx,DWORD PTR [eax]
  5831e8:	8b f8                	mov    edi,eax
  5831ea:	ff 52 68             	call   DWORD PTR [edx+0x68]
  5831ed:	85 c0                	test   eax,eax
  5831ef:	db e2                	fnclex
  5831f1:	7d 0f                	jge    0x583202
  5831f3:	6a 68                	push   0x68
  5831f5:	68 6c cd 40 00       	push   0x40cd6c
  5831fa:	57                   	push   edi
  5831fb:	50                   	push   eax
  5831fc:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583202:	8b 7d c0             	mov    edi,DWORD PTR [ebp-0x40]
  583205:	8b 45 d4             	mov    eax,DWORD PTR [ebp-0x2c]
  583208:	50                   	push   eax
  583209:	57                   	push   edi
  58320a:	8b 17                	mov    edx,DWORD PTR [edi]
  58320c:	ff 52 74             	call   DWORD PTR [edx+0x74]
  58320f:	85 c0                	test   eax,eax
  583211:	db e2                	fnclex
  583213:	7d 0f                	jge    0x583224
  583215:	6a 74                	push   0x74
  583217:	68 fc d5 40 00       	push   0x40d5fc
  58321c:	57                   	push   edi
  58321d:	50                   	push   eax
  58321e:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583224:	8d 4d dc             	lea    ecx,[ebp-0x24]
  583227:	8d 55 e0             	lea    edx,[ebp-0x20]
  58322a:	51                   	push   ecx
  58322b:	8d 45 e4             	lea    eax,[ebp-0x1c]
  58322e:	52                   	push   edx
  58322f:	50                   	push   eax
  583230:	6a 03                	push   0x3
  583232:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  583238:	8b 0e                	mov    ecx,DWORD PTR [esi]
  58323a:	83 c4 10             	add    esp,0x10
  58323d:	56                   	push   esi
  58323e:	ff 91 7c 05 00 00    	call   DWORD PTR [ecx+0x57c]
  583244:	8d 55 e4             	lea    edx,[ebp-0x1c]
  583247:	50                   	push   eax
  583248:	52                   	push   edx
  583249:	ff d3                	call   ebx
  58324b:	8b f8                	mov    edi,eax
  58324d:	6a ff                	push   0xffffffff
  58324f:	57                   	push   edi
  583250:	8b 07                	mov    eax,DWORD PTR [edi]
  583252:	ff 90 8c 00 00 00    	call   DWORD PTR [eax+0x8c]
  583258:	85 c0                	test   eax,eax
  58325a:	db e2                	fnclex
  58325c:	7d 12                	jge    0x583270
  58325e:	68 8c 00 00 00       	push   0x8c
  583263:	68 fc d5 40 00       	push   0x40d5fc
  583268:	57                   	push   edi
  583269:	50                   	push   eax
  58326a:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583270:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  583273:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  583279:	8b 0e                	mov    ecx,DWORD PTR [esi]
  58327b:	56                   	push   esi
  58327c:	ff 91 70 05 00 00    	call   DWORD PTR [ecx+0x570]
  583282:	8d 55 e4             	lea    edx,[ebp-0x1c]
  583285:	50                   	push   eax
  583286:	52                   	push   edx
  583287:	ff d3                	call   ebx
  583289:	8b 5d 0c             	mov    ebx,DWORD PTR [ebp+0xc]
  58328c:	8b f0                	mov    esi,eax
  58328e:	0f bf 0b             	movsx  ecx,WORD PTR [ebx]
  583291:	8b 3e                	mov    edi,DWORD PTR [esi]
  583293:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  58329a:	2b c1                	sub    eax,ecx
  58329c:	8b 0d c0 ed 63 00    	mov    ecx,DWORD PTR ds:0x63edc0
  5832a2:	8d 04 80             	lea    eax,[eax+eax*4]
  5832a5:	8b 94 81 84 00 00 00 	mov    edx,DWORD PTR [ecx+eax*4+0x84]
  5832ac:	52                   	push   edx
  5832ad:	ff 15 34 10 40 00    	call   DWORD PTR ds:0x401034
  5832b3:	8b d0                	mov    edx,eax
  5832b5:	8d 4d e8             	lea    ecx,[ebp-0x18]
  5832b8:	ff 15 3c 12 40 00    	call   DWORD PTR ds:0x40123c
  5832be:	50                   	push   eax
  5832bf:	56                   	push   esi
  5832c0:	ff 57 54             	call   DWORD PTR [edi+0x54]
  5832c3:	85 c0                	test   eax,eax
  5832c5:	db e2                	fnclex
  5832c7:	7d 0f                	jge    0x5832d8
  5832c9:	6a 54                	push   0x54
  5832cb:	68 0c d6 40 00       	push   0x40d60c
  5832d0:	56                   	push   esi
  5832d1:	50                   	push   eax
  5832d2:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5832d8:	8d 4d e8             	lea    ecx,[ebp-0x18]
  5832db:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  5832e1:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  5832e4:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  5832ea:	66 8b 03             	mov    ax,WORD PTR [ebx]
  5832ed:	66 a3 6a c7 63 00    	mov    ds:0x63c76a,ax
  5832f3:	eb 47                	jmp    0x58333c
  5832f5:	66 c7 05 6a c7 63 00 	mov    WORD PTR ds:0x63c76a,0xffff
  5832fc:	ff ff 
  5832fe:	8b 0e                	mov    ecx,DWORD PTR [esi]
  583300:	56                   	push   esi
  583301:	ff 91 7c 05 00 00    	call   DWORD PTR [ecx+0x57c]
  583307:	8d 55 e4             	lea    edx,[ebp-0x1c]
  58330a:	50                   	push   eax
  58330b:	52                   	push   edx
  58330c:	ff d3                	call   ebx
  58330e:	8b f0                	mov    esi,eax
  583310:	6a 00                	push   0x0
  583312:	56                   	push   esi
  583313:	8b 06                	mov    eax,DWORD PTR [esi]
  583315:	ff 90 8c 00 00 00    	call   DWORD PTR [eax+0x8c]
  58331b:	85 c0                	test   eax,eax
  58331d:	db e2                	fnclex
  58331f:	7d 12                	jge    0x583333
  583321:	68 8c 00 00 00       	push   0x8c
  583326:	68 fc d5 40 00       	push   0x40d5fc
  58332b:	56                   	push   esi
  58332c:	50                   	push   eax
  58332d:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583333:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  583336:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  58333c:	ba 54 cf 40 00       	mov    edx,0x40cf54
  583341:	8d 4d e8             	lea    ecx,[ebp-0x18]
  583344:	ff 15 d8 11 40 00    	call   DWORD PTR ds:0x4011d8
  58334a:	8d 4d e8             	lea    ecx,[ebp-0x18]
  58334d:	51                   	push   ecx
  58334e:	e8 6d 37 0b 00       	call   0x636ac0
  583353:	8d 4d e8             	lea    ecx,[ebp-0x18]
  583356:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  58335c:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
  583363:	9b                   	fwait
  583364:	68 8d 33 58 00       	push   0x58338d
  583369:	eb 21                	jmp    0x58338c
  58336b:	8d 4d e8             	lea    ecx,[ebp-0x18]
  58336e:	ff 15 80 12 40 00    	call   DWORD PTR ds:0x401280
  583374:	8d 55 dc             	lea    edx,[ebp-0x24]
  583377:	8d 45 e0             	lea    eax,[ebp-0x20]
  58337a:	52                   	push   edx
  58337b:	8d 4d e4             	lea    ecx,[ebp-0x1c]
  58337e:	50                   	push   eax
  58337f:	51                   	push   ecx
  583380:	6a 03                	push   0x3
  583382:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  583388:	83 c4 10             	add    esp,0x10
  58338b:	c3                   	ret
  58338c:	c3                   	ret
  58338d:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  583390:	50                   	push   eax
  583391:	8b 10                	mov    edx,DWORD PTR [eax]
  583393:	ff 52 08             	call   DWORD PTR [edx+0x8]
  583396:	8b 45 fc             	mov    eax,DWORD PTR [ebp-0x4]
  583399:	8b 4d ec             	mov    ecx,DWORD PTR [ebp-0x14]
  58339c:	5f                   	pop    edi
  58339d:	5e                   	pop    esi
  58339e:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  5833a5:	5b                   	pop    ebx
  5833a6:	8b e5                	mov    esp,ebp
  5833a8:	5d                   	pop    ebp
  5833a9:	c2 18 00             	ret    0x18
  5833ac:	90                   	nop
  5833ad:	90                   	nop
  5833ae:	90                   	nop
  5833af:	90                   	nop
  5833b0:	55                   	push   ebp
  5833b1:	8b ec                	mov    ebp,esp
  5833b3:	83 ec 0c             	sub    esp,0xc
  5833b6:	68 06 32 40 00       	push   0x403206
  5833bb:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  5833c1:	50                   	push   eax
  5833c2:	64 89 25 00 00 00 00 	mov    DWORD PTR fs:0x0,esp
  5833c9:	83 ec 54             	sub    esp,0x54
  5833cc:	53                   	push   ebx
  5833cd:	56                   	push   esi
  5833ce:	57                   	push   edi
  5833cf:	89 65 f4             	mov    DWORD PTR [ebp-0xc],esp
  5833d2:	c7 45 f8 20 1c 40 00 	mov    DWORD PTR [ebp-0x8],0x401c20
  5833d9:	8b 75 08             	mov    esi,DWORD PTR [ebp+0x8]
  5833dc:	8b c6                	mov    eax,esi
  5833de:	83 e0 01             	and    eax,0x1
  5833e1:	89 45 fc             	mov    DWORD PTR [ebp-0x4],eax
  5833e4:	83 e6 fe             	and    esi,0xfffffffe
  5833e7:	56                   	push   esi
  5833e8:	89 75 08             	mov    DWORD PTR [ebp+0x8],esi
  5833eb:	8b 0e                	mov    ecx,DWORD PTR [esi]
  5833ed:	ff 51 04             	call   DWORD PTR [ecx+0x4]
  5833f0:	8b 16                	mov    edx,DWORD PTR [esi]
  5833f2:	33 c0                	xor    eax,eax
  5833f4:	56                   	push   esi
  5833f5:	89 45 e0             	mov    DWORD PTR [ebp-0x20],eax
  5833f8:	89 45 dc             	mov    DWORD PTR [ebp-0x24],eax
  5833fb:	89 45 d8             	mov    DWORD PTR [ebp-0x28],eax
  5833fe:	89 45 d4             	mov    DWORD PTR [ebp-0x2c],eax
  583401:	89 45 d0             	mov    DWORD PTR [ebp-0x30],eax
  583404:	89 45 cc             	mov    DWORD PTR [ebp-0x34],eax
  583407:	ff 92 24 04 00 00    	call   DWORD PTR [edx+0x424]
  58340d:	8b 1d bc 10 40 00    	mov    ebx,DWORD PTR ds:0x4010bc
  583413:	50                   	push   eax
  583414:	8d 45 e0             	lea    eax,[ebp-0x20]
  583417:	50                   	push   eax
  583418:	ff d3                	call   ebx
  58341a:	8b f8                	mov    edi,eax
  58341c:	8d 55 d4             	lea    edx,[ebp-0x2c]
  58341f:	52                   	push   edx
  583420:	57                   	push   edi
  583421:	8b 0f                	mov    ecx,DWORD PTR [edi]
  583423:	ff 91 98 00 00 00    	call   DWORD PTR [ecx+0x98]
  583429:	85 c0                	test   eax,eax
  58342b:	db e2                	fnclex
  58342d:	7d 12                	jge    0x583441
  58342f:	68 98 00 00 00       	push   0x98
  583434:	68 b4 d5 40 00       	push   0x40d5b4
  583439:	57                   	push   edi
  58343a:	50                   	push   eax
  58343b:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583441:	33 c0                	xor    eax,eax
  583443:	66 83 7d d4 ff       	cmp    WORD PTR [ebp-0x2c],0xffff
  583448:	8d 4d e0             	lea    ecx,[ebp-0x20]
  58344b:	0f 94 c0             	sete   al
  58344e:	f7 d8                	neg    eax
  583450:	66 8b f8             	mov    di,ax
  583453:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  583459:	66 85 ff             	test   di,di
  58345c:	0f 85 35 03 00 00    	jne    0x583797
  583462:	8b 0e                	mov    ecx,DWORD PTR [esi]
  583464:	56                   	push   esi
  583465:	ff 91 24 04 00 00    	call   DWORD PTR [ecx+0x424]
  58346b:	8d 55 e0             	lea    edx,[ebp-0x20]
  58346e:	50                   	push   eax
  58346f:	52                   	push   edx
  583470:	ff d3                	call   ebx
  583472:	8b f8                	mov    edi,eax
  583474:	8d 4d d4             	lea    ecx,[ebp-0x2c]
  583477:	51                   	push   ecx
  583478:	57                   	push   edi
  583479:	8b 07                	mov    eax,DWORD PTR [edi]
  58347b:	ff 90 98 00 00 00    	call   DWORD PTR [eax+0x98]
  583481:	85 c0                	test   eax,eax
  583483:	db e2                	fnclex
  583485:	7d 12                	jge    0x583499
  583487:	68 98 00 00 00       	push   0x98
  58348c:	68 b4 d5 40 00       	push   0x40d5b4
  583491:	57                   	push   edi
  583492:	50                   	push   eax
  583493:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583499:	33 d2                	xor    edx,edx
  58349b:	66 83 7d d4 ff       	cmp    WORD PTR [ebp-0x2c],0xffff
  5834a0:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5834a3:	0f 94 c2             	sete   dl
  5834a6:	f7 da                	neg    edx
  5834a8:	66 8b fa             	mov    di,dx
  5834ab:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  5834b1:	66 85 ff             	test   di,di
  5834b4:	0f 85 dd 02 00 00    	jne    0x583797
  5834ba:	8b 06                	mov    eax,DWORD PTR [esi]
  5834bc:	56                   	push   esi
  5834bd:	ff 90 6c 05 00 00    	call   DWORD PTR [eax+0x56c]
  5834c3:	8d 4d d8             	lea    ecx,[ebp-0x28]
  5834c6:	50                   	push   eax
  5834c7:	51                   	push   ecx
  5834c8:	ff d3                	call   ebx
  5834ca:	8b f8                	mov    edi,eax
  5834cc:	8d 45 cc             	lea    eax,[ebp-0x34]
  5834cf:	50                   	push   eax
  5834d0:	57                   	push   edi
  5834d1:	8b 17                	mov    edx,DWORD PTR [edi]
  5834d3:	ff 52 78             	call   DWORD PTR [edx+0x78]
  5834d6:	85 c0                	test   eax,eax
  5834d8:	db e2                	fnclex
  5834da:	7d 0f                	jge    0x5834eb
  5834dc:	6a 78                	push   0x78
  5834de:	68 b4 d5 40 00       	push   0x40d5b4
  5834e3:	57                   	push   edi
  5834e4:	50                   	push   eax
  5834e5:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5834eb:	8b 0e                	mov    ecx,DWORD PTR [esi]
  5834ed:	56                   	push   esi
  5834ee:	ff 91 78 05 00 00    	call   DWORD PTR [ecx+0x578]
  5834f4:	8d 55 e0             	lea    edx,[ebp-0x20]
  5834f7:	50                   	push   eax
  5834f8:	52                   	push   edx
  5834f9:	ff d3                	call   ebx
  5834fb:	8b 55 0c             	mov    edx,DWORD PTR [ebp+0xc]
  5834fe:	8d 4d dc             	lea    ecx,[ebp-0x24]
  583501:	8b f8                	mov    edi,eax
  583503:	51                   	push   ecx
  583504:	66 8b 0a             	mov    cx,WORD PTR [edx]
  583507:	8b 07                	mov    eax,DWORD PTR [edi]
  583509:	51                   	push   ecx
  58350a:	57                   	push   edi
  58350b:	ff 50 40             	call   DWORD PTR [eax+0x40]
  58350e:	85 c0                	test   eax,eax
  583510:	db e2                	fnclex
  583512:	7d 0f                	jge    0x583523
  583514:	6a 40                	push   0x40
  583516:	68 c4 d5 40 00       	push   0x40d5c4
  58351b:	57                   	push   edi
  58351c:	50                   	push   eax
  58351d:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583523:	8b 45 dc             	mov    eax,DWORD PTR [ebp-0x24]
  583526:	8d 4d d0             	lea    ecx,[ebp-0x30]
  583529:	51                   	push   ecx
  58352a:	50                   	push   eax
  58352b:	8b 10                	mov    edx,DWORD PTR [eax]
  58352d:	8b f8                	mov    edi,eax
  58352f:	ff 52 68             	call   DWORD PTR [edx+0x68]
  583532:	85 c0                	test   eax,eax
  583534:	db e2                	fnclex
  583536:	7d 0f                	jge    0x583547
  583538:	6a 68                	push   0x68
  58353a:	68 6c cd 40 00       	push   0x40cd6c
  58353f:	57                   	push   edi
  583540:	50                   	push   eax
  583541:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583547:	d9 45 cc             	fld    DWORD PTR [ebp-0x34]
  58354a:	d8 45 d0             	fadd   DWORD PTR [ebp-0x30]
  58354d:	ff 15 20 12 40 00    	call   DWORD PTR ds:0x401220
  583553:	8b f8                	mov    edi,eax
  583555:	8d 55 d8             	lea    edx,[ebp-0x28]
  583558:	8d 45 dc             	lea    eax,[ebp-0x24]
  58355b:	52                   	push   edx
  58355c:	8d 4d e0             	lea    ecx,[ebp-0x20]
  58355f:	50                   	push   eax
  583560:	51                   	push   ecx
  583561:	6a 03                	push   0x3
  583563:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  583569:	8b 16                	mov    edx,DWORD PTR [esi]
  58356b:	83 c4 10             	add    esp,0x10
  58356e:	56                   	push   esi
  58356f:	ff 92 3c 05 00 00    	call   DWORD PTR [edx+0x53c]
  583575:	50                   	push   eax
  583576:	8d 45 e0             	lea    eax,[ebp-0x20]
  583579:	50                   	push   eax
  58357a:	ff d3                	call   ebx
  58357c:	8b d8                	mov    ebx,eax
  58357e:	8d 55 d0             	lea    edx,[ebp-0x30]
  583581:	52                   	push   edx
  583582:	53                   	push   ebx
  583583:	8b 0b                	mov    ecx,DWORD PTR [ebx]
  583585:	ff 91 88 00 00 00    	call   DWORD PTR [ecx+0x88]
  58358b:	85 c0                	test   eax,eax
  58358d:	db e2                	fnclex
  58358f:	7d 12                	jge    0x5835a3
  583591:	68 88 00 00 00       	push   0x88
  583596:	68 b4 d5 40 00       	push   0x40d5b4
  58359b:	53                   	push   ebx
  58359c:	50                   	push   eax
  58359d:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5835a3:	d9 45 d0             	fld    DWORD PTR [ebp-0x30]
  5835a6:	ff 15 20 12 40 00    	call   DWORD PTR ds:0x401220
  5835ac:	8b d8                	mov    ebx,eax
  5835ae:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5835b1:	89 5d e4             	mov    DWORD PTR [ebp-0x1c],ebx
  5835b4:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  5835ba:	03 df                	add    ebx,edi
  5835bc:	66 81 fb c2 01       	cmp    bx,0x1c2
  5835c1:	7e 3c                	jle    0x5835ff
  5835c3:	8b 06                	mov    eax,DWORD PTR [esi]
  5835c5:	56                   	push   esi
  5835c6:	ff 90 3c 05 00 00    	call   DWORD PTR [eax+0x53c]
  5835cc:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5835cf:	50                   	push   eax
  5835d0:	51                   	push   ecx
  5835d1:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  5835d7:	8b d8                	mov    ebx,eax
  5835d9:	8b 45 e4             	mov    eax,DWORD PTR [ebp-0x1c]
  5835dc:	2b f8                	sub    edi,eax
  5835de:	83 ef 14             	sub    edi,0x14
  5835e1:	8b 13                	mov    edx,DWORD PTR [ebx]
  5835e3:	0f bf c7             	movsx  eax,di
  5835e6:	89 45 a4             	mov    DWORD PTR [ebp-0x5c],eax
  5835e9:	db 45 a4             	fild   DWORD PTR [ebp-0x5c]
  5835ec:	d9 5d a0             	fstp   DWORD PTR [ebp-0x60]
  5835ef:	8b 4d a0             	mov    ecx,DWORD PTR [ebp-0x60]
  5835f2:	51                   	push   ecx
  5835f3:	53                   	push   ebx
  5835f4:	ff 52 7c             	call   DWORD PTR [edx+0x7c]
  5835f7:	85 c0                	test   eax,eax
  5835f9:	db e2                	fnclex
  5835fb:	7d 46                	jge    0x583643
  5835fd:	eb 35                	jmp    0x583634
  5835ff:	8b 16                	mov    edx,DWORD PTR [esi]
  583601:	56                   	push   esi
  583602:	ff 92 3c 05 00 00    	call   DWORD PTR [edx+0x53c]
  583608:	50                   	push   eax
  583609:	8d 45 e0             	lea    eax,[ebp-0x20]
  58360c:	50                   	push   eax
  58360d:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  583613:	83 c7 32             	add    edi,0x32
  583616:	8b d8                	mov    ebx,eax
  583618:	0f bf d7             	movsx  edx,di
  58361b:	89 55 9c             	mov    DWORD PTR [ebp-0x64],edx
  58361e:	8b 0b                	mov    ecx,DWORD PTR [ebx]
  583620:	db 45 9c             	fild   DWORD PTR [ebp-0x64]
  583623:	d9 5d 98             	fstp   DWORD PTR [ebp-0x68]
  583626:	8b 45 98             	mov    eax,DWORD PTR [ebp-0x68]
  583629:	50                   	push   eax
  58362a:	53                   	push   ebx
  58362b:	ff 51 7c             	call   DWORD PTR [ecx+0x7c]
  58362e:	85 c0                	test   eax,eax
  583630:	db e2                	fnclex
  583632:	7d 0f                	jge    0x583643
  583634:	6a 7c                	push   0x7c
  583636:	68 b4 d5 40 00       	push   0x40d5b4
  58363b:	53                   	push   ebx
  58363c:	50                   	push   eax
  58363d:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583643:	8d 4d e0             	lea    ecx,[ebp-0x20]
  583646:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  58364c:	8b 4d 0c             	mov    ecx,DWORD PTR [ebp+0xc]
  58364f:	0f bf 09             	movsx  ecx,WORD PTR [ecx]
  583652:	8d 04 cd 00 00 00 00 	lea    eax,[ecx*8+0x0]
  583659:	2b c1                	sub    eax,ecx
  58365b:	8d 14 80             	lea    edx,[eax+eax*4]
  58365e:	a1 c0 ed 63 00       	mov    eax,ds:0x63edc0
  583663:	8b 4c 90 2c          	mov    ecx,DWORD PTR [eax+edx*4+0x2c]
  583667:	51                   	push   ecx
  583668:	ff 15 4c 10 40 00    	call   DWORD PTR ds:0x40104c
  58366e:	8b 16                	mov    edx,DWORD PTR [esi]
  583670:	83 f8 01             	cmp    eax,0x1
  583673:	56                   	push   esi
  583674:	7f 44                	jg     0x5836ba
  583676:	ff 92 3c 05 00 00    	call   DWORD PTR [edx+0x53c]
  58367c:	50                   	push   eax
  58367d:	8d 45 e0             	lea    eax,[ebp-0x20]
  583680:	50                   	push   eax
  583681:	ff 15 bc 10 40 00    	call   DWORD PTR ds:0x4010bc
  583687:	8b f0                	mov    esi,eax
  583689:	6a 00                	push   0x0
  58368b:	56                   	push   esi
  58368c:	8b 0e                	mov    ecx,DWORD PTR [esi]
  58368e:	ff 91 9c 00 00 00    	call   DWORD PTR [ecx+0x9c]
  583694:	85 c0                	test   eax,eax
  583696:	db e2                	fnclex
  583698:	7d 12                	jge    0x5836ac
  58369a:	68 9c 00 00 00       	push   0x9c
  58369f:	68 b4 d5 40 00       	push   0x40d5b4
  5836a4:	56                   	push   esi
  5836a5:	50                   	push   eax
  5836a6:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5836ac:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5836af:	ff 15 84 12 40 00    	call   DWORD PTR ds:0x401284
  5836b5:	e9 dd 00 00 00       	jmp    0x583797
  5836ba:	ff 92 78 05 00 00    	call   DWORD PTR [edx+0x578]
  5836c0:	8b 1d bc 10 40 00    	mov    ebx,DWORD PTR ds:0x4010bc
  5836c6:	50                   	push   eax
  5836c7:	8d 45 dc             	lea    eax,[ebp-0x24]
  5836ca:	50                   	push   eax
  5836cb:	ff d3                	call   ebx
  5836cd:	8b f8                	mov    edi,eax
  5836cf:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]
  5836d2:	8d 55 d8             	lea    edx,[ebp-0x28]
  5836d5:	8b 0f                	mov    ecx,DWORD PTR [edi]
  5836d7:	52                   	push   edx
  5836d8:	66 8b 10             	mov    dx,WORD PTR [eax]
  5836db:	52                   	push   edx
  5836dc:	57                   	push   edi
  5836dd:	ff 51 40             	call   DWORD PTR [ecx+0x40]
  5836e0:	85 c0                	test   eax,eax
  5836e2:	db e2                	fnclex
  5836e4:	7d 0f                	jge    0x5836f5
  5836e6:	6a 40                	push   0x40
  5836e8:	68 c4 d5 40 00       	push   0x40d5c4
  5836ed:	57                   	push   edi
  5836ee:	50                   	push   eax
  5836ef:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  5836f5:	8b 45 d8             	mov    eax,DWORD PTR [ebp-0x28]
  5836f8:	8d 55 cc             	lea    edx,[ebp-0x34]
  5836fb:	52                   	push   edx
  5836fc:	50                   	push   eax
  5836fd:	8b 08                	mov    ecx,DWORD PTR [eax]
  5836ff:	8b f8                	mov    edi,eax
  583701:	ff 51 60             	call   DWORD PTR [ecx+0x60]
  583704:	85 c0                	test   eax,eax
  583706:	db e2                	fnclex
  583708:	7d 0f                	jge    0x583719
  58370a:	6a 60                	push   0x60
  58370c:	68 6c cd 40 00       	push   0x40cd6c
  583711:	57                   	push   edi
  583712:	50                   	push   eax
  583713:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583719:	8b 06                	mov    eax,DWORD PTR [esi]
  58371b:	56                   	push   esi
  58371c:	ff 90 6c 05 00 00    	call   DWORD PTR [eax+0x56c]
  583722:	8d 4d e0             	lea    ecx,[ebp-0x20]
  583725:	50                   	push   eax
  583726:	51                   	push   ecx
  583727:	ff d3                	call   ebx
  583729:	8b f8                	mov    edi,eax
  58372b:	8d 45 d0             	lea    eax,[ebp-0x30]
  58372e:	50                   	push   eax
  58372f:	57                   	push   edi
  583730:	8b 17                	mov    edx,DWORD PTR [edi]
  583732:	ff 52 70             	call   DWORD PTR [edx+0x70]
  583735:	85 c0                	test   eax,eax
  583737:	db e2                	fnclex
  583739:	7d 0f                	jge    0x58374a
  58373b:	6a 70                	push   0x70
  58373d:	68 b4 d5 40 00       	push   0x40d5b4
  583742:	57                   	push   edi
  583743:	50                   	push   eax
  583744:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  58374a:	d9 45 cc             	fld    DWORD PTR [ebp-0x34]
  58374d:	d8 45 d0             	fadd   DWORD PTR [ebp-0x30]
  583750:	8b 3e                	mov    edi,DWORD PTR [esi]
  583752:	d8 05 98 15 40 00    	fadd   DWORD PTR ds:0x401598
  583758:	ff 15 20 12 40 00    	call   DWORD PTR ds:0x401220
  58375e:	8b 4d 0c             	mov    ecx,DWORD PTR [ebp+0xc]
  583761:	50                   	push   eax
  583762:	51                   	push   ecx
  583763:	56                   	push   esi
  583764:	ff 97 10 07 00 00    	call   DWORD PTR [edi+0x710]
  58376a:	85 c0                	test   eax,eax
  58376c:	7d 12                	jge    0x583780
  58376e:	68 10 07 00 00       	push   0x710
  583773:	68 44 be 40 00       	push   0x40be44
  583778:	56                   	push   esi
  583779:	50                   	push   eax
  58377a:	ff 15 98 10 40 00    	call   DWORD PTR ds:0x401098
  583780:	8d 55 d8             	lea    edx,[ebp-0x28]
  583783:	8d 45 dc             	lea    eax,[ebp-0x24]
  583786:	52                   	push   edx
  583787:	8d 4d e0             	lea    ecx,[ebp-0x20]
  58378a:	50                   	push   eax
  58378b:	51                   	push   ecx
  58378c:	6a 03                	push   0x3
  58378e:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  583794:	83 c4 10             	add    esp,0x10
  583797:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
  58379e:	9b                   	fwait
  58379f:	68 bf 37 58 00       	push   0x5837bf
  5837a4:	eb 18                	jmp    0x5837be
  5837a6:	8d 55 d8             	lea    edx,[ebp-0x28]
  5837a9:	8d 45 dc             	lea    eax,[ebp-0x24]
  5837ac:	52                   	push   edx
  5837ad:	8d 4d e0             	lea    ecx,[ebp-0x20]
  5837b0:	50                   	push   eax
  5837b1:	51                   	push   ecx
  5837b2:	6a 03                	push   0x3
  5837b4:	ff 15 68 10 40 00    	call   DWORD PTR ds:0x401068
  5837ba:	83 c4 10             	add    esp,0x10
  5837bd:	c3                   	ret
  5837be:	c3                   	ret
  5837bf:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
  5837c2:	50                   	push   eax
  5837c3:	8b 10                	mov    edx,DWORD PTR [eax]
  5837c5:	ff 52 08             	call   DWORD PTR [edx+0x8]
  5837c8:	8b 45 fc             	mov    eax,DWORD PTR [ebp-0x4]
  5837cb:	8b 4d ec             	mov    ecx,DWORD PTR [ebp-0x14]
  5837ce:	5f                   	pop    edi
  5837cf:	5e                   	pop    esi
  5837d0:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  5837d7:	5b                   	pop    ebx
  5837d8:	8b e5                	mov    esp,ebp
  5837da:	5d                   	pop    ebp
  5837db:	c2 18 00             	ret    0x18
  5837de:	90                   	nop
  5837df:	90                   	nop
