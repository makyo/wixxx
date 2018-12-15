/loaded wixxx.tf
;;;;;
; wixxx logging
;
; Sets up commands and triggers for logging wixxx flags.
;
; Note that you'll need some variables set for this. You should have another
; wixxx-info.tf file that you load in .tfrc looking something like:
; 
; /set WIXXX_USER=wixxx_username
; /set WIXXX_SECRET=wwixxx_secret
; /export WIXXX_USER
; /export WIXXX_SECRET
; /set wixxx_python=/path/to/wixxx/venv/bin/python
; /set wixxx_client=/path/to/wixxx/wixxx-client.py
; /set wixxx_server=https://wixxx.vis.adjectivespecies.com

/def create_wixxx_write = /def -F -p2 -ag -mregexp -t"^(.+)$$" wixxx_write = \
	$do_wixxx_write

/def do_wixxx_write = \
	/if (wixxx_fh != -1) \
		/test tfwrite(wixxx_fh, {P1})%; \
	/endif

/def create_wixxx_stop = /def -F -p3 -ag -mregexp -t"^(-------------------------------------------------------- by K'T/AnnonyMouse --)$$" wixxx_stop = \
	$do_wixxx_stop

/def do_wixxx_stop = \
	/if (wixxx_fh != -1) \
		/test tfwrite(wixxx_fh, {P1})%; \
		/test tfclose(wixxx_fh)%; \
	/endif%; \
	/set wixxx_fh=-1 %; \
	/undef wixxx_write%; \
	/undef wixxx_stop%; \
	/eval /quote /echo :::wixxx-client: !%%{wixxx_python} %%{wixxx_client} --server %%{wixxx_server} %%{logname} && rm %%{logname}

/def logwixxx = \
	/eval /set logname /tmp/wixxx.${world_name}.$[ftime("%@")]%; \
	/set wixxx_fh=$[tfopen(logname, "w")]%; \
	/if (wixxx_fh != -1) \
		/create_wixxx_write%; \
		/create_wixxx_stop%; \
;/eval /echo :::wixxx: %{*}%; \
		/send wixxx %{*}%; \
	/endif

/def wixxx_trigger = \
	/def -F -p2 -mregexp -t%{*} = /logwixxx %%{P1}
